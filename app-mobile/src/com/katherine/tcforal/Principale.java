package com.katherine.tcforal;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.media.AudioManager;
import android.media.MediaRecorder;
import android.media.MediaScannerConnection;
import android.media.ToneGenerator;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.SystemClock;
import android.os.Vibrator;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileInputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;

/**
 * TCF Canada — expression orale.
 *
 * Un seul geste : je touche la tâche. L'appli fait tout le reste —
 * elle compte le temps, elle m'enregistre, elle s'arrête toute seule.
 * Aucune connexion n'est nécessaire : tout se passe dans le téléphone.
 */
public class Principale extends Activity {

    // ---------------------------------------------------------------
    // Les 3 tâches du vrai examen (12 min en tout). Les temps sont ici.
    // ---------------------------------------------------------------
    private static final int[]    NUM   = { 1, 2, 3 };
    private static final String[] NOM   = { "Présentation personnelle",
                                            "Interaction — je pose les questions",
                                            "Argumentation — mon point de vue" };
    private static final int[]    PREP  = { 0, 120, 0 };     // secondes de préparation
    private static final int[]    DUREE = { 120, 210, 270 }; // secondes de parole
    private static final int[]    COUL  = { 0xFF4FD1C5, 0xFFF6AD55, 0xFFF56565 };

    private static final int FOND = 0xFF0D0F14, CARTE = 0xFF171B24,
                             TEXTE = 0xFFF2F4F8, GRIS = 0xFF8B93A7, ROUGE = 0xFFF56565;

    private static final int[]    VOL_TONE = { 25, 60, 100 };
    private static final String[] VOL_NOM  = { "doux", "moyen", "fort" };

    // Où envoyer les enregistrements : le point d'accès WiFi du PC (adresse fixe
    // de nmcli). Si le PC n'est pas joignable, le fichier reste sur le téléphone.
    private static final String SERVEUR = "http://10.42.0.1:8777";
    // Clé secrète : la même que dans serveur_eval.py. Sans elle, le PC refuse.
    private static final String CLE = "T7f2Ka9pQx4Lm3Zr";

    // ---------------------------------------------------------------
    private FrameLayout racine;
    private View ecranAccueil, ecranChrono, ecranFini;
    private TextView vPhase, vTitre, vTemps, vEtape, vFiniTitre, vFiniDetail, vAvertissement;
    private TextView vEtatPC, vEtatSujet, vSujetAccueil, vSujet;
    private Anneau anneau;
    private FrameLayout blocAnneau;
    private LinearLayout colChrono;
    private Button bSon, bVolume, bVib, bSuivante, bEnvoyer, bSujet;

    // Le sujet tiré sur l'ordinateur, gardé dans le téléphone. Une fois chargé,
    // il reste disponible même loin du WiFi — pour enregistrer dans le patio.
    private String sujetT2 = "", sujetT3 = "";
    private int sujetN;
    private int sujetT2i = -1, sujetT3i = -1;  // la combinaison en cours
    private boolean sujetVisible;   // masqué par défaut : pas de spoiler avant l'oral
    private boolean occupe;         // un envoi est déjà en cours

    private MediaRecorder rec;
    private File fichier;
    private final Handler h = new Handler();
    private ToneGenerator tonalites;
    private Vibrator vibreur;

    private int idx;              // tâche en cours
    private long finPhase;        // horloge de fin de la phase en cours
    private int dureePhase;       // secondes de la phase en cours
    private boolean enregistre;   // cette phase est-elle enregistrée ?
    private boolean actif;

    private final java.util.Random alea = new java.util.Random();

    private SharedPreferences prefs;
    private boolean son = true, vibration = true;
    private int volume = 1;

    // ===============================================================
    // Démarrage
    // ===============================================================
    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        prefs = getSharedPreferences("tcf", MODE_PRIVATE);
        son       = prefs.getBoolean("son", true);
        vibration = prefs.getBoolean("vibration", true);
        volume    = prefs.getInt("volume", 1);
        sujetT2   = prefs.getString("sujetT2", "");
        sujetT3   = prefs.getString("sujetT3", "");
        sujetN    = prefs.getInt("sujetN", 0);
        sujetT2i  = prefs.getInt("sujetT2i", -1);
        sujetT3i  = prefs.getInt("sujetT3i", -1);
        oublierSujetPerime();

        vibreur = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);

        racine = new FrameLayout(this);
        racine.setBackgroundColor(FOND);
        construireAccueil();
        construireChrono();
        construireFini();
        setContentView(racine);
        montrer(ecranAccueil);

        demanderPermissions();
    }

    /**
     * La banque de sujets a changé (textes corrigés) : la question gardée dans
     * le téléphone peut être un vieil énoncé qui n'existe plus. On l'oublie
     * plutôt que de l'afficher — sinon on réviserait un texte périmé.
     */
    private void oublierSujetPerime() {
        if (sujetN == 0) return;
        if (contient(Sujets.TACHE2, sujetT2) && contient(Sujets.TACHE3, sujetT3)) return;
        sujetT2 = ""; sujetT3 = ""; sujetN = 0; sujetT2i = -1; sujetT3i = -1;
        prefs.edit().remove("sujetT2").remove("sujetT3").remove("sujetN")
                    .remove("sujetT2i").remove("sujetT3i").apply();
    }

    private static int indexDe(String[] banque, String texte) {
        for (int i = 0; i < banque.length; i++) if (banque[i].equals(texte)) return i;
        return -1;
    }

    private static boolean contient(String[] banque, String texte) {
        return indexDe(banque, texte) >= 0;
    }

    private void demanderPermissions() {
        if (Build.VERSION.SDK_INT < 23) return;
        boolean micro = checkSelfPermission(android.Manifest.permission.RECORD_AUDIO)
                        == PackageManager.PERMISSION_GRANTED;
        boolean disque = checkSelfPermission(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                         == PackageManager.PERMISSION_GRANTED;
        if (!micro || !disque) {
            requestPermissions(new String[]{
                    android.Manifest.permission.RECORD_AUDIO,
                    android.Manifest.permission.WRITE_EXTERNAL_STORAGE }, 1);
        } else {
            vAvertissement.setVisibility(View.GONE);
        }
    }

    @Override
    public void onRequestPermissionsResult(int code, String[] perms, int[] resultats) {
        boolean tout = resultats.length > 0;
        for (int r : resultats) if (r != PackageManager.PERMISSION_GRANTED) tout = false;
        vAvertissement.setVisibility(tout ? View.GONE : View.VISIBLE);
    }

    // ===============================================================
    // Écran d'accueil : les 3 tâches
    // ===============================================================
    private void construireAccueil() {
        LinearLayout col = colonne();
        col.setPadding(dp(18), dp(22), dp(18), dp(22));

        col.addView(texte("🎙️  TCF — Expression orale", 20, TEXTE, true));
        TextView sous = texte("Je touche la tâche, je pose le téléphone, je parle.\n"
                + "Ça enregistre et ça s'arrête tout seul.", 14, GRIS, false);
        sous.setPadding(0, dp(6), 0, dp(20));
        col.addView(sous);

        // La question d'abord : on la tire, PUIS on fait les tâches.
        col.addView(carteQuestion());

        TextView sep = texte("Les 3 tâches", 13, GRIS, true);
        sep.setPadding(0, dp(22), 0, dp(10));
        col.addView(sep);
        for (int i = 0; i < NUM.length; i++) col.addView(carteTache(i));

        col.addView(cartePC());

        // réglages du son
        LinearLayout reglages = new LinearLayout(this);
        reglages.setOrientation(LinearLayout.HORIZONTAL);
        reglages.setPadding(0, dp(20), 0, 0);
        bSon = petitBouton(son ? "🔊 Son" : "🔇 Son", new View.OnClickListener() {
            public void onClick(View v) {
                son = !son;
                prefs.edit().putBoolean("son", son).apply();
                bSon.setText(son ? "🔊 Son" : "🔇 Son");
                styliserPetit(bSon, son);
            }
        });
        bVolume = petitBouton(VOL_NOM[volume], new View.OnClickListener() {
            public void onClick(View v) {
                volume = (volume + 1) % 3;
                prefs.edit().putInt("volume", volume).apply();
                bVolume.setText(VOL_NOM[volume]);
                styliserPetit(bVolume, volume != 0);
            }
        });
        bVib = petitBouton("📳", new View.OnClickListener() {
            public void onClick(View v) {
                vibration = !vibration;
                prefs.edit().putBoolean("vibration", vibration).apply();
                styliserPetit(bVib, vibration);
            }
        });
        styliserPetit(bSon, son);
        styliserPetit(bVolume, volume != 0);
        styliserPetit(bVib, vibration);
        reglages.addView(bSon); reglages.addView(bVolume); reglages.addView(bVib);
        col.addView(reglages);

        vAvertissement = texte("⚠️ Il me faut le micro et le stockage. "
                + "Paramètres → Applications → TCF Oral → Autorisations.", 13, ROUGE, false);
        vAvertissement.setPadding(0, dp(16), 0, 0);
        col.addView(vAvertissement);

        TextView note = texte("Les bips sortent par le haut-parleur, donc ils sont dans "
                + "l'enregistrement — ça marque le début et la fin, ce n'est pas grave. "
                + "Avec des écouteurs filaires SANS micro, ils ne s'entendent que dans mon oreille.\n\n"
                + "Les fichiers vont dans le dossier TCF_oral/ du téléphone.", 12, GRIS, false);
        note.setPadding(0, dp(18), 0, 0);
        col.addView(note);

        ScrollView sc = new ScrollView(this);
        sc.addView(col);
        ecranAccueil = sc;
        racine.addView(sc);
    }

    private View carteTache(final int i) {
        LinearLayout carte = new LinearLayout(this);
        carte.setOrientation(LinearLayout.HORIZONTAL);
        carte.setGravity(Gravity.CENTER_VERTICAL);
        carte.setPadding(dp(18), dp(18), dp(18), dp(18));
        GradientDrawable fond = new GradientDrawable();
        fond.setColor(CARTE);
        fond.setCornerRadius(dp(14));
        carte.setBackground(fond);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(12);
        carte.setLayoutParams(lp);

        TextView numero = texte(String.valueOf(NUM[i]), 30, COUL[i], true);
        numero.setWidth(dp(42));
        carte.addView(numero);

        LinearLayout txt = new LinearLayout(this);
        txt.setOrientation(LinearLayout.VERTICAL);
        txt.addView(texte(NOM[i], 16, TEXTE, true));
        txt.addView(texte((PREP[i] > 0 ? mmss(PREP[i]) + " de préparation, puis " : "")
                + mmss(DUREE[i]) + " de parole", 13, GRIS, false));
        carte.addView(txt);

        carte.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) { lancer(i); }
        });
        return carte;
    }

    /** Une carte du même style que les tâches. */
    private LinearLayout carte() {
        LinearLayout c = new LinearLayout(this);
        c.setOrientation(LinearLayout.VERTICAL);
        c.setPadding(dp(18), dp(16), dp(18), dp(16));
        GradientDrawable fond = new GradientDrawable();
        fond.setColor(CARTE);
        fond.setCornerRadius(dp(14));
        c.setBackground(fond);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dp(10);
        c.setLayoutParams(lp);
        return c;
    }

    /**
     * « Ma question » : le tirage vit ici, dans le téléphone. Aucun réseau,
     * aucun ordinateur — je peux tirer une question dans le patio.
     */
    private View carteQuestion() {
        LinearLayout carte = carte();
        carte.addView(texte("🎲  Ma question", 16, TEXTE, true));
        TextView aide = texte("Je tire ici, hors ligne. Tirer ne PERD rien : "
                + "une question ne sort du pot que quand je l'ai enregistrée "
                + "en entier, sans l'arrêter. Sinon elle revient plus tard.",
                12, GRIS, false);
        aide.setPadding(0, dp(4), 0, dp(12));
        carte.addView(aide);

        bSujet = grosBouton("🎲  Tirer une question", 0xFF1B2418, new View.OnClickListener() {
            public void onClick(View v) { tirerSujet(); }
        });
        carte.addView(bSujet);

        vEtatSujet = texte("", 12, GRIS, false);
        vEtatSujet.setPadding(0, dp(4), 0, 0);
        carte.addView(vEtatSujet);

        // La question reste masquée ici : on la découvre pendant l'épreuve,
        // comme le jour J. Un toucher la révèle si j'en ai vraiment besoin.
        vSujetAccueil = texte("", 12, GRIS, false);
        vSujetAccueil.setPadding(0, dp(8), 0, 0);
        vSujetAccueil.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) { sujetVisible = !sujetVisible; majEtatPC(); }
        });
        carte.addView(vSujetAccueil);
        return carte;
    }

    /**
     * « Mon ordinateur » : le SEUL endroit qui a besoin du WiFi, et seulement
     * quand je le demande. Le PC ne sert plus qu'à regarder ce que j'ai fait.
     */
    private View cartePC() {
        LinearLayout carte = carte();
        carte.addView(texte("💻  Mon ordinateur", 16, TEXTE, true));
        TextView aide = texte("Pour aller voir mes enregistrements sur le grand écran. "
                + "Branche le WiFi « TCF-PC », appuie, puis tu peux le rééteindre.",
                12, GRIS, false);
        aide.setPadding(0, dp(4), 0, dp(12));
        carte.addView(aide);

        bEnvoyer = grosBouton("📤  Envoyer au PC", 0xFF16202E, new View.OnClickListener() {
            public void onClick(View v) { envoyerEnAttente(); }
        });
        carte.addView(bEnvoyer);

        vEtatPC = texte("", 12, GRIS, false);
        vEtatPC.setPadding(0, dp(4), 0, 0);
        carte.addView(vEtatPC);
        return carte;
    }

    /** Rafraîchit les libellés des deux cartes. */
    private void majEtatPC() {
        if (bEnvoyer == null) return;
        int attente = fichiersLocaux().length - dejaEnvoyes().size();
        if (attente < 0) attente = 0;
        bEnvoyer.setText(attente > 0 ? "📤  Envoyer au PC  (" + attente + ")"
                                     : "📤  Envoyer au PC");
        if (sujetN == 0) {
            vSujetAccueil.setText("Aucune question tirée. Appuie sur le bouton "
                    + "ci-dessus avant de commencer.");
        } else if (!sujetVisible) {
            String faites = tachesFaites();
            vSujetAccueil.setText("🔒 Question #" + sujetN + " prête — elle s'affichera "
                    + "pendant les tâches 2 et 3. (Toucher pour la voir maintenant.)"
                    + (faites.length() > 0
                       ? "\n✅ Déjà enregistré : tâche " + faites : ""));
        } else {
            vSujetAccueil.setText("Question #" + sujetN + "\n\n💬 Tâche 2 — " + sujetT2
                    + "\n\n🗣 Tâche 3 — " + sujetT3 + "\n\n(Toucher pour masquer.)");
        }
    }

    // ===============================================================
    // Écran chrono
    // ===============================================================
    private void construireChrono() {
        LinearLayout col = colonne();
        col.setGravity(Gravity.CENTER_HORIZONTAL);
        col.setPadding(dp(16), dp(16), dp(16), dp(16));

        vPhase = texte("JE PARLE", 16, GRIS, true);
        vPhase.setGravity(Gravity.CENTER);
        col.addView(vPhase);

        vTitre = texte("", 14, GRIS, false);
        vTitre.setGravity(Gravity.CENTER);
        vTitre.setPadding(0, dp(4), 0, dp(12));
        col.addView(vTitre);

        // L'énoncé, pendant que je parle. Comme le jour J : je l'ai sous les yeux
        // pour les tâches 2 et 3, rien pour la présentation personnelle.
        // Gros, aéré, plein cadre : pendant l'épreuve on lit du coin de l'œil,
        // le téléphone posé sur la table. Trop petit = illisible = temps perdu.
        vSujet = texte("", 20, TEXTE, false);
        vSujet.setLineSpacing(0, 1.32f);
        vSujet.setPadding(dp(16), dp(16), dp(16), dp(16));
        GradientDrawable cadre = new GradientDrawable();
        cadre.setColor(CARTE);
        cadre.setCornerRadius(dp(12));
        vSujet.setBackground(cadre);
        LinearLayout.LayoutParams lps = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lps.bottomMargin = dp(14);
        vSujet.setLayoutParams(lps);
        col.addView(vSujet);

        blocAnneau = new FrameLayout(this);
        FrameLayout bloc = blocAnneau;
        int taille = tailleAnneau(false);
        anneau = new Anneau(this);
        bloc.addView(anneau, new FrameLayout.LayoutParams(taille, taille));

        LinearLayout centre = new LinearLayout(this);
        centre.setOrientation(LinearLayout.VERTICAL);
        centre.setGravity(Gravity.CENTER);
        vTemps = texte("0:00", 62, TEXTE, true);
        vTemps.setGravity(Gravity.CENTER);
        centre.addView(vTemps);
        vEtape = texte("", 13, GRIS, false);
        vEtape.setGravity(Gravity.CENTER);
        centre.addView(vEtape);
        bloc.addView(centre, new FrameLayout.LayoutParams(taille, taille));

        LinearLayout.LayoutParams lpa = new LinearLayout.LayoutParams(taille, taille);
        lpa.gravity = Gravity.CENTER_HORIZONTAL;
        col.addView(bloc, lpa);

        Button annuler = grosBouton("■  Annuler", 0xFF2B1B1E, new View.OnClickListener() {
            public void onClick(View v) { arreter(true); montrer(ecranAccueil); }
        });
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.topMargin = dp(20);
        col.addView(annuler, lp);

        // Avec l'énoncé affiché, l'écran peut devenir plus haut que le téléphone :
        // on rend la colonne défilable pour ne jamais couper le chrono.
        ScrollView sc = new ScrollView(this);
        sc.setFillViewport(true);
        sc.addView(col);
        colChrono = col;
        ecranChrono = sc;
        racine.addView(sc);
    }

    /** Diamètre de l'anneau : plus petit quand l'énoncé partage l'écran. */
    private int tailleAnneau(boolean avecSujet) {
        return (int) (getResources().getDisplayMetrics().widthPixels
                      * (avecSujet ? 0.42 : 0.74));
    }

    /** Redimensionne l'anneau selon qu'un énoncé est affiché ou non. */
    private void reglerAnneau(boolean avecSujet) {
        // Sans énoncé (tâche 1) le chrono se pose au milieu de l'écran ; avec
        // énoncé, tout remonte en haut pour que le texte commence à la
        // première ligne visible, sans avoir à faire défiler.
        colChrono.setGravity(avecSujet ? Gravity.TOP | Gravity.CENTER_HORIZONTAL
                                       : Gravity.CENTER);
        ecranChrono.post(new Runnable() {
            public void run() { ((ScrollView) ecranChrono).scrollTo(0, 0); }
        });
        int t = tailleAnneau(avecSujet);
        anneau.setLayoutParams(new FrameLayout.LayoutParams(t, t));
        blocAnneau.getChildAt(1).setLayoutParams(new FrameLayout.LayoutParams(t, t));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(t, t);
        lp.gravity = Gravity.CENTER_HORIZONTAL;
        blocAnneau.setLayoutParams(lp);
        vTemps.setTextSize(avecSujet ? 38 : 62);
    }

    // ===============================================================
    // Écran de fin
    // ===============================================================
    private void construireFini() {
        LinearLayout col = colonne();
        col.setGravity(Gravity.CENTER);
        col.setPadding(dp(24), dp(24), dp(24), dp(24));

        col.addView(centrer(texte("✅", 54, TEXTE, false)));
        vFiniTitre = centrer(texte("", 21, TEXTE, true));
        col.addView(vFiniTitre);
        vFiniDetail = centrer(texte("", 13, GRIS, false));
        vFiniDetail.setPadding(0, dp(8), 0, dp(28));
        col.addView(vFiniDetail);

        bSuivante = grosBouton("Tâche suivante  ▶", 0xFF18241C, new View.OnClickListener() {
            public void onClick(View v) { lancer(idx + 1); }
        });
        col.addView(bSuivante);

        Button refaire = grosBouton("↻  Refaire", CARTE, new View.OnClickListener() {
            public void onClick(View v) { lancer(idx); }
        });
        col.addView(refaire);

        Button accueil = grosBouton("Accueil", CARTE, new View.OnClickListener() {
            public void onClick(View v) { montrer(ecranAccueil); }
        });
        col.addView(accueil);

        ecranFini = col;
        racine.addView(col);
    }

    // ===============================================================
    // Le déroulé d'une tâche
    // ===============================================================
    private void lancer(int i) {
        if (i >= NUM.length) { montrer(ecranAccueil); return; }
        if (Build.VERSION.SDK_INT >= 23
                && checkSelfPermission(android.Manifest.permission.RECORD_AUDIO)
                   != PackageManager.PERMISSION_GRANTED) {
            demanderPermissions();
            Toast.makeText(this, "Il me faut le micro pour t'enregistrer.", Toast.LENGTH_LONG).show();
            return;
        }
        arreter(true);
        idx = i;
        actif = true;
        ouvrirTonalites();
        vTitre.setText("Tâche " + NUM[i] + " — " + NOM[i]);

        // L'énoncé n'apparaît qu'au moment où il sert : la tâche 1 est une
        // présentation personnelle, il n'y a rien à lire. Les tâches 2 et 3 ont
        // leur texte sous les yeux, comme au vrai examen.
        String enonce = (i == 1) ? sujetT2 : (i == 2) ? sujetT3 : "";
        if (enonce.length() > 0) {
            vSujet.setText(enonce);
            vSujet.setVisibility(View.VISIBLE);
        } else {
            vSujet.setVisibility(View.GONE);
        }
        reglerAnneau(enonce.length() > 0);

        montrer(ecranChrono);

        if (PREP[i] > 0) demarrerPhase("PRÉPARATION", PREP[i], false);
        else             demarrerPhase("JE PARLE", DUREE[i], true);
    }

    /** Une phase = préparation (silencieuse) ou parole (enregistrée). */
    private void demarrerPhase(String nom, final int secondes, boolean avecMicro) {
        dureePhase = secondes;
        enregistre = avecMicro;
        vPhase.setText(nom);
        vEtape.setText(avecMicro ? "🔴 j'enregistre · " + mmss(secondes) + " en tout"
                                 : "je prépare · " + mmss(secondes) + " en tout");

        if (avecMicro && !demarrerMicro(secondes)) return;

        // On laisse 400 ms au micro pour s'ouvrir : rien du début n'est perdu.
        h.postDelayed(new Runnable() {
            public void run() {
                if (!actif) return;
                finPhase = SystemClock.elapsedRealtime() + secondes * 1000L;
                if (enregistre) { bip(ToneGenerator.TONE_PROP_BEEP2, 300); vibrer(new long[]{0,180,120,180}); }
                else            { bip(ToneGenerator.TONE_PROP_BEEP, 180);  vibrer(new long[]{0,200}); }
                programmerAvertissements(secondes);
                h.post(battement);
            }
        }, avecMicro ? 400 : 0);
    }

    /** Les bips qui me disent où j'en suis, sans regarder l'écran. */
    private void programmerAvertissements(int secondes) {
        if (secondes >= 150) plusTard((secondes - 60) * 1000L, ToneGenerator.TONE_PROP_BEEP, 200, new long[]{0,250});
        if (secondes >= 60)  plusTard((secondes - 30) * 1000L, ToneGenerator.TONE_PROP_BEEP2, 250, new long[]{0,150,100,150});
        for (int s = 5; s >= 1; s--)
            plusTard((secondes - s) * 1000L, ToneGenerator.TONE_PROP_BEEP, 70, null);
    }

    private void plusTard(long quand, final int ton, final int duree, final long[] vibr) {
        h.postDelayed(new Runnable() {
            public void run() {
                if (!actif) return;
                bip(ton, duree);
                if (vibr != null) vibrer(vibr);
            }
        }, quand);
    }

    /** Rafraîchit l'affichage et déclenche la suite quand la phase est finie. */
    private final Runnable battement = new Runnable() {
        public void run() {
            if (!actif) return;
            long reste = finPhase - SystemClock.elapsedRealtime();
            if (reste <= 0) { finPhaseAtteinte(); return; }
            vTemps.setText(mmss((int) Math.ceil(reste / 1000.0)));
            float part = 1f - (reste / (dureePhase * 1000f));
            anneau.regler(part, reste <= 30000 ? ROUGE : COUL[idx]);
            h.postDelayed(this, 100);
        }
    };

    private void finPhaseAtteinte() {
        if (!enregistre) {                 // la préparation est finie → je parle
            bip(ToneGenerator.TONE_PROP_ACK, 400);
            demarrerPhase("JE PARLE", DUREE[idx], true);
            return;
        }
        terminer(true);
    }

    /**
     * complet = false quand quelque chose m'a interrompue (appel, écran éteint) :
     * on garde quand même ce qui est déjà enregistré — on n'efface jamais ma voix.
     */
    private void terminer(boolean complet) {
        if (!enregistre) {          // interrompue pendant la préparation : rien à garder
            arreter(false);
            montrer(ecranAccueil);
            return;
        }
        int parle = complet ? DUREE[idx]
                            : DUREE[idx] - (int) Math.max(0, (finPhase - SystemClock.elapsedRealtime()) / 1000);
        String nom = fermerMicro();
        actif = false;
        h.removeCallbacksAndMessages(null);
        if (complet) {
            bip(ToneGenerator.TONE_PROP_NACK, 900);
            vibrer(new long[]{0, 400, 150, 400, 150, 600});
        }
        h.postDelayed(new Runnable() { public void run() { fermerTonalites(); } }, 1500);

        vFiniTitre.setText(complet ? "Tâche " + NUM[idx] + " terminée"
                                   : "Tâche " + NUM[idx] + " interrompue");
        vFiniDetail.setText(nom == null
                ? "⚠️ L'enregistrement n'a pas marché."
                : mmss(parle) + " de parole" + (complet ? "" : " (coupée)")
                  + "\nenregistré dans TCF_oral/\n" + nom);
        bSuivante.setVisibility(idx < NUM.length - 1 ? View.VISIBLE : View.GONE);
        montrer(ecranFini);
        if (nom != null && fichier != null) {
            // D'abord le carnet du téléphone : il ne dépend d'aucun réseau.
            noterLocalement(nom, NUM[idx], parle, complet);
            televerser(fichier, nom);
        }
    }

    /**
     * Envoie l'enregistrement au PC, en tâche de fond. Le réseau est facultatif :
     * si le point d'accès du PC n'est pas là, on ne fait rien de plus — le fichier
     * est déjà gardé dans TCF_oral/ et pourra partir la prochaine fois.
     */
    private void televerser(final File f, final String nom) {
        new Thread(new Runnable() { public void run() {
            boolean ok = false;
            HttpURLConnection c = null;
            try {
                URL url = new URL(SERVEUR + "/oral/envoyer?nom="
                        + URLEncoder.encode(nom, "UTF-8") + "&sujet=" + sujetN);
                c = (HttpURLConnection) url.openConnection();
                c.setConnectTimeout(4000);
                c.setReadTimeout(20000);
                c.setRequestMethod("POST");
                c.setDoOutput(true);
                c.setFixedLengthStreamingMode((int) f.length());
                c.setRequestProperty("Content-Type", "application/octet-stream");
                c.setRequestProperty("X-Cle", CLE);   // clé dans l'en-tête, pas l'URL
                OutputStream os = c.getOutputStream();
                FileInputStream in = new FileInputStream(f);
                byte[] tampon = new byte[8192];
                int lu;
                while ((lu = in.read(tampon)) != -1) os.write(tampon, 0, lu);
                in.close();
                os.flush();
                os.close();
                ok = (c.getResponseCode() == 200);
            } catch (Exception e) {
                ok = false;
            } finally {
                if (c != null) c.disconnect();
            }
            final boolean envoye = ok;
            if (ok) marquerEnvoye(nom);
            runOnUiThread(new Runnable() { public void run() {
                vFiniDetail.append(envoye
                        ? "\n✅ envoyé au PC"
                        : "\n📱 gardé sur le téléphone — appuie sur « Envoyer au PC » "
                          + "en revenant près de l'ordinateur");
                majEtatPC();
            }});
        }}).start();
    }

    // ===============================================================
    // Le PC : renvoi des enregistrements en attente, et le sujet du jour
    // ===============================================================

    /**
     * Garde, DANS LE TÉLÉPHONE, l'énoncé à côté de l'audio.
     *
     * C'est ici que la simulation a vraiment lieu : le téléphone ne doit pas
     * dépendre de l'ordinateur pour savoir quelle question va avec quelle voix.
     * Deux fichiers dans TCF_oral/ :
     *   • registre.json      — pour l'appli (et pour l'envoi au PC)
     *   • mes-simulations.txt — pour mes yeux, lisible depuis n'importe quel
     *     explorateur de fichiers, même sans l'appli.
     */
    private void noterLocalement(String nomAudio, int tache, int secondes, boolean complet) {
        File dossier = new File(Environment.getExternalStorageDirectory(), "TCF_oral");
        try {
            dossier.mkdirs();

            org.json.JSONObject reg = new org.json.JSONObject();
            File fReg = new File(dossier, "registre.json");
            if (fReg.exists()) {
                try { reg = new org.json.JSONObject(lireTexte(fReg)); }
                catch (Exception ignore) { reg = new org.json.JSONObject(); }
            }
            org.json.JSONObject e = new org.json.JSONObject();
            e.put("sujet", sujetN);
            e.put("tache", tache);
            e.put("t2", sujetT2);
            e.put("t3", sujetT3);
            // les index de la combinaison : c'est eux qui disent si CETTE
            // question a été travaillée, indépendamment du numéro de tirage
            e.put("t2i", sujetT2i);
            e.put("t3i", sujetT3i);
            e.put("secondes", secondes);
            e.put("complet", complet);
            e.put("date", horodatageLisible());
            reg.put(nomAudio, e);
            ecrireTexte(fReg, reg.toString(1), false);

            StringBuilder s = new StringBuilder();
            s.append(horodatageLisible()).append("  ·  Tâche ").append(tache);
            s.append(sujetN > 0 ? "  ·  Sujet #" + sujetN : "  ·  (sans sujet chargé)");
            s.append("\n  🎙 ").append(nomAudio);
            s.append(complet ? "  (complète)" : "  (COUPÉE — ne compte pas)").append("\n");
            if (tache == 2 && sujetT2.length() > 0) s.append("  💬 ").append(sujetT2).append("\n");
            if (tache == 3 && sujetT3.length() > 0) s.append("  🗣 ").append(sujetT3).append("\n");
            s.append("\n");
            ecrireTexte(new File(dossier, "mes-simulations.txt"), s.toString(), true);
        } catch (Exception ignore) {
            // l'audio est sauvé : c'est le principal, le carnet peut attendre
        }
    }

    private String lireTexte(File f) throws Exception {
        FileInputStream in = new FileInputStream(f);
        java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
        byte[] t = new byte[4096];
        int lu;
        while ((lu = in.read(t)) != -1) out.write(t, 0, lu);
        in.close();
        return out.toString("UTF-8");
    }

    private void ecrireTexte(File f, String contenu, boolean ajouter) throws Exception {
        java.io.FileOutputStream o = new java.io.FileOutputStream(f, ajouter);
        o.write(contenu.getBytes("UTF-8"));
        o.close();
    }

    private static String horodatageLisible() {
        return new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm", java.util.Locale.US)
                .format(new java.util.Date());
    }

    /** Quelles tâches ai-je déjà enregistrées pour le sujet chargé ? */
    private String tachesFaites() {
        if (sujetN == 0) return "";
        File f = new File(new File(Environment.getExternalStorageDirectory(), "TCF_oral"),
                          "registre.json");
        if (!f.exists()) return "";
        try {
            org.json.JSONObject reg = new org.json.JSONObject(lireTexte(f));
            java.util.TreeSet<Integer> t = new java.util.TreeSet<Integer>();
            java.util.Iterator<String> it = reg.keys();
            while (it.hasNext()) {
                org.json.JSONObject e = reg.getJSONObject(it.next());
                if (e.optInt("sujet") == sujetN) t.add(e.optInt("tache"));
            }
            if (t.isEmpty()) return "";
            StringBuilder s = new StringBuilder();
            for (Integer x : t) { if (s.length() > 0) s.append(", "); s.append(x); }
            return s.toString();
        } catch (Exception e) {
            return "";
        }
    }

    /** Le dossier des enregistrements, tel qu'il est sur le téléphone. */
    private File[] fichiersLocaux() {
        File dossier = new File(Environment.getExternalStorageDirectory(), "TCF_oral");
        File[] f = dossier.listFiles();
        if (f == null) return new File[0];
        java.util.List<File> audios = new java.util.ArrayList<File>();
        for (File x : f)
            if (x.isFile() && x.getName().toLowerCase(java.util.Locale.US).endsWith(".m4a")
                && x.length() > 0)
                audios.add(x);
        java.util.Collections.sort(audios, new java.util.Comparator<File>() {
            public int compare(File a, File b) { return a.getName().compareTo(b.getName()); }
        });
        return audios.toArray(new File[0]);
    }

    /** Ce que le téléphone sait déjà avoir livré (mémoire locale, hors ligne). */
    private java.util.Set<String> dejaEnvoyes() {
        return new java.util.HashSet<String>(
                prefs.getStringSet("envoyes", new java.util.HashSet<String>()));
    }

    private void marquerEnvoye(String nom) {
        java.util.Set<String> s = dejaEnvoyes();
        s.add(nom);
        prefs.edit().putStringSet("envoyes", s).apply();
    }

    /** Un GET sur le PC, avec la clé. Renvoie le corps, ou null si injoignable. */
    private String lireDuPC(String chemin) {
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(SERVEUR + chemin).openConnection();
            c.setConnectTimeout(4000);
            c.setReadTimeout(10000);
            c.setRequestProperty("X-Cle", CLE);
            if (c.getResponseCode() != 200) return null;
            java.io.InputStream in = c.getInputStream();
            java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
            byte[] tampon = new byte[4096];
            int lu;
            while ((lu = in.read(tampon)) != -1) out.write(tampon, 0, lu);
            in.close();
            return out.toString("UTF-8");
        } catch (Exception e) {
            return null;
        } finally {
            if (c != null) c.disconnect();
        }
    }

    /**
     * Le bouton « Envoyer au PC ». Il demande d'abord au PC ce qu'il a déjà,
     * puis n'envoie que ce qui manque — on peut appuyer dix fois sans créer de
     * doublon. C'est ce qui permet d'enregistrer dans le patio, loin du point
     * d'accès, et de tout remonter en revenant près de l'ordinateur.
     */
    private void envoyerEnAttente() {
        if (occupe) return;
        final File[] locaux = fichiersLocaux();
        if (locaux.length == 0) {
            vEtatPC.setText("Rien à envoyer : aucun enregistrement sur le téléphone.");
            return;
        }
        occupe = true;
        bEnvoyer.setEnabled(false);
        vEtatPC.setText("Je cherche le PC…");

        new Thread(new Runnable() { public void run() {
            String rep = lireDuPC("/oral/liste");
            if (rep == null) {
                fini("❌ PC injoignable. Vérifie le WiFi « TCF-PC » et que "
                     + "serveur_eval.py tourne.");
                return;
            }
            // Ce que le PC possède déjà : on ne renvoie jamais ça.
            java.util.Set<String> surPC = new java.util.HashSet<String>();
            try {
                org.json.JSONArray liste =
                        new org.json.JSONObject(rep).getJSONArray("fichiers");
                for (int i = 0; i < liste.length(); i++)
                    surPC.add(liste.getJSONObject(i).getString("nom"));
            } catch (Exception e) {
                fini("❌ Réponse du PC illisible.");
                return;
            }

            int envoyes = 0, echecs = 0, deja = 0;
            for (int i = 0; i < locaux.length; i++) {
                final File f = locaux[i];
                if (surPC.contains(f.getName())) { deja++; marquerEnvoye(f.getName()); continue; }
                final int n = i + 1;
                dire("Envoi " + n + "/" + locaux.length + " — " + f.getName());
                if (envoyerFichier(f)) { envoyes++; marquerEnvoye(f.getName()); }
                else echecs++;
            }

            // Le carnet part avec les audios : c'est lui qui porte les questions,
            // donc c'est lui qui permet au PC d'afficher quoi va avec quoi.
            boolean carnet = envoyerCarnet();

            String bilan;
            if (envoyes == 0 && echecs == 0)
                bilan = "✅ Tout est déjà sur le PC (" + deja + " enregistrement"
                        + (deja > 1 ? "s" : "") + ").";
            else
                bilan = "✅ " + envoyes + " envoyé" + (envoyes > 1 ? "s" : "")
                        + (deja > 0 ? " · " + deja + " déjà là" : "")
                        + (echecs > 0 ? " · ⚠️ " + echecs + " échec"
                                        + (echecs > 1 ? "s" : "") : "");
            fini(bilan + (carnet ? "" : " · ⚠️ carnet non transmis"));
        }}).start();
    }

    /**
     * Tire une question, ICI, sans réseau.
     *
     * Le téléphone garde la liste des combinaisons déjà sorties : il n'en
     * redonne jamais une deux fois tant qu'il en reste des neuves. Quand les
     * 264 sont passées, il le dit et repart pour un tour.
     */
    /**
     * Les énoncés vraiment TRAVAILLÉS, tâche par tâche.
     *
     * Les tâches 2 et 3 ont chacune leur pot : l'énoncé de la tâche 2 change
     * à chaque tirage, que celui de la tâche 3 change ou non. Tirer ne
     * consomme rien — ce qui retire un énoncé du pot, c'est de l'avoir fait,
     * un enregistrement complet sur SA tâche. (La tâche 1 est une présentation
     * personnelle : elle ne dépend d'aucun énoncé.)
     *
     * On compare les TEXTES, pas les numéros : la banque de sujets change, et
     * un vieux numéro ne désigne plus le même énoncé. Le texte, lui, reste.
     *
     * On le relit du carnet à chaque tirage : la vérité, ce sont les audios.
     */
    private java.util.Set<Integer> enoncesTravailles(int tache) {
        java.util.Set<Integer> faits = new java.util.HashSet<Integer>();
        String[] banque = (tache == 2) ? Sujets.TACHE2 : Sujets.TACHE3;
        String champ    = (tache == 2) ? "t2" : "t3";
        File f = new File(new File(Environment.getExternalStorageDirectory(), "TCF_oral"),
                          "registre.json");
        if (!f.exists()) return faits;
        try {
            org.json.JSONObject reg = new org.json.JSONObject(lireTexte(f));
            java.util.Iterator<String> it = reg.keys();
            while (it.hasNext()) {
                org.json.JSONObject e = reg.getJSONObject(it.next());
                if (e.optInt("tache") != tache) continue;  // la 1 ne dépend d'aucun énoncé
                if (!e.optBoolean("complet")) continue;    // coupée : ça ne compte pas
                String texte = e.optString(champ, "");
                for (int i = 0; i < banque.length; i++)
                    if (banque[i].equals(texte)) { faits.add(i); break; }
            }
        } catch (Exception ignore) { }
        return faits;
    }

    /**
     * Un énoncé au hasard parmi ceux qui restent à travailler.
     * Jamais celui qu'on a sous les yeux : « tirer » doit toujours changer
     * quelque chose, sinon on croit que le bouton ne marche pas.
     */
    private int tirerDans(String[] banque, java.util.Set<Integer> faits, int encours) {
        java.util.List<Integer> libres = new java.util.ArrayList<Integer>();
        for (int i = 0; i < banque.length; i++)
            if (!faits.contains(i) && i != encours) libres.add(i);
        if (libres.isEmpty())                        // tout fait : on repart pour un tour
            for (int i = 0; i < banque.length; i++)
                if (i != encours) libres.add(i);
        return libres.get(alea.nextInt(libres.size()));
    }

    private void tirerSujet() {
        java.util.Set<Integer> faits2 = enoncesTravailles(2);
        java.util.Set<Integer> faits3 = enoncesTravailles(3);

        int enCours2 = (sujetN > 0) ? sujetT2i : -1;
        int enCours3 = (sujetN > 0) ? sujetT3i : -1;
        sujetT2i = tirerDans(Sujets.TACHE2, faits2, enCours2);
        sujetT3i = tirerDans(Sujets.TACHE3, faits3, enCours3);
        sujetT2  = Sujets.TACHE2[sujetT2i];
        sujetT3  = Sujets.TACHE3[sujetT3i];
        sujetN   = prefs.getInt("compteur", 0) + 1;
        sujetVisible = false;
        prefs.edit().putString("sujetT2", sujetT2)
                    .putString("sujetT3", sujetT3)
                    .putInt("sujetN", sujetN)
                    .putInt("compteur", sujetN)
                    .putInt("sujetT2i", sujetT2i)
                    .putInt("sujetT3i", sujetT3i).apply();

        int reste2 = Sujets.TACHE2.length - faits2.size();
        int reste3 = Sujets.TACHE3.length - faits3.size();
        vEtatSujet.setText("🎲 Question #" + sujetN + " tirée."
                + "\nÀ travailler : " + reste2 + " énoncés de tâche 2, "
                + reste3 + " de tâche 3.");
        majEtatPC();
    }

    /**
     * Envoie le carnet (registre.json) au PC.
     *
     * C'est ce qui fait du PC un simple tableau de bord : il ne tire plus rien,
     * il reçoit ce que le téléphone a fait — question comprise — et l'affiche.
     */
    private boolean envoyerCarnet() {
        File f = new File(new File(Environment.getExternalStorageDirectory(), "TCF_oral"),
                          "registre.json");
        if (!f.exists()) return true;          // rien à dire, ce n'est pas un échec
        HttpURLConnection c = null;
        try {
            byte[] corps = lireTexte(f).getBytes("UTF-8");
            c = (HttpURLConnection) new URL(SERVEUR + "/oral/journal").openConnection();
            c.setConnectTimeout(4000);
            c.setReadTimeout(15000);
            c.setRequestMethod("POST");
            c.setDoOutput(true);
            c.setFixedLengthStreamingMode(corps.length);
            c.setRequestProperty("Content-Type", "application/json");
            c.setRequestProperty("X-Cle", CLE);
            OutputStream os = c.getOutputStream();
            os.write(corps);
            os.flush();
            os.close();
            return c.getResponseCode() == 200;
        } catch (Exception e) {
            return false;
        } finally {
            if (c != null) c.disconnect();
        }
    }

    /** Envoie un fichier ; true si le PC l'a bien reçu. */
    private boolean envoyerFichier(File f) {
        HttpURLConnection c = null;
        try {
            // On joint le numéro du sujet affiché : c'est ce qui permet à
            // l'ordinateur de savoir quel énoncé va avec quelle voix.
            URL url = new URL(SERVEUR + "/oral/envoyer?nom="
                    + URLEncoder.encode(f.getName(), "UTF-8") + "&sujet=" + sujetN);
            c = (HttpURLConnection) url.openConnection();
            c.setConnectTimeout(4000);
            c.setReadTimeout(30000);
            c.setRequestMethod("POST");
            c.setDoOutput(true);
            c.setFixedLengthStreamingMode((int) f.length());
            c.setRequestProperty("Content-Type", "application/octet-stream");
            c.setRequestProperty("X-Cle", CLE);
            OutputStream os = c.getOutputStream();
            FileInputStream in = new FileInputStream(f);
            byte[] tampon = new byte[8192];
            int lu;
            while ((lu = in.read(tampon)) != -1) os.write(tampon, 0, lu);
            in.close();
            os.flush();
            os.close();
            return c.getResponseCode() == 200;
        } catch (Exception e) {
            return false;
        } finally {
            if (c != null) c.disconnect();
        }
    }

    /** Message d'avancement, depuis le fil réseau. */
    private void dire(final String msg) {
        runOnUiThread(new Runnable() { public void run() { vEtatPC.setText(msg); } });
    }

    /** Fin d'une opération réseau : message, boutons réactivés, compteur à jour. */
    private void fini(final String msg) {
        runOnUiThread(new Runnable() { public void run() {
            occupe = false;
            bEnvoyer.setEnabled(true);
            bSujet.setEnabled(true);
            vEtatPC.setText(msg);
            majEtatPC();
        }});
    }

    /** Coupe tout. jeter = true → on efface l'enregistrement en cours. */
    private void arreter(boolean jeter) {
        actif = false;
        h.removeCallbacksAndMessages(null);
        String nom = fermerMicro();
        if (jeter && nom != null && fichier != null) fichier.delete();
        fermerTonalites();
        if (vibreur != null) vibreur.cancel();
    }

    // ===============================================================
    // Le micro
    // ===============================================================
    private boolean demarrerMicro(int secondes) {
        try {
            File dossier = new File(Environment.getExternalStorageDirectory(), "TCF_oral");
            dossier.mkdirs();
            fichier = new File(dossier, "tache-" + NUM[idx] + "_" + horodatage() + ".m4a");

            rec = new MediaRecorder();
            rec.setAudioSource(MediaRecorder.AudioSource.MIC);
            rec.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
            rec.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
            rec.setAudioSamplingRate(44100);
            rec.setAudioEncodingBitRate(128000);
            rec.setMaxDuration((secondes + 5) * 1000);   // filet de sécurité
            rec.setOutputFile(fichier.getAbsolutePath());
            rec.prepare();
            rec.start();
            return true;
        } catch (Exception e) {
            rec = null;
            Toast.makeText(this, "Micro impossible : " + e.getMessage(), Toast.LENGTH_LONG).show();
            arreter(true);
            montrer(ecranAccueil);
            return false;
        }
    }

    /** Ferme proprement et renvoie le nom du fichier écrit (ou null). */
    private String fermerMicro() {
        if (rec == null) return null;
        String nom = null;
        try {
            rec.stop();
            if (fichier != null && fichier.length() > 0) {
                nom = fichier.getName();
                // pour que le fichier apparaisse tout de suite dans l'explorateur
                MediaScannerConnection.scanFile(this,
                        new String[]{ fichier.getAbsolutePath() },
                        new String[]{ "audio/mp4" }, null);
            }
        } catch (Exception e) {
            if (fichier != null) fichier.delete();
        } finally {
            try { rec.release(); } catch (Exception ignore) {}
            rec = null;
        }
        return nom;
    }

    // ===============================================================
    // Bips et vibrations
    // ===============================================================
    private void ouvrirTonalites() {
        fermerTonalites();
        try {
            tonalites = new ToneGenerator(AudioManager.STREAM_MUSIC, VOL_TONE[volume]);
        } catch (Exception e) { tonalites = null; }
    }

    private void fermerTonalites() {
        if (tonalites != null) { try { tonalites.release(); } catch (Exception ignore) {} tonalites = null; }
    }

    private void bip(int ton, int duree) {
        if (!son || tonalites == null) return;
        try { tonalites.startTone(ton, duree); } catch (Exception ignore) {}
    }

    private void vibrer(long[] motif) {
        if (!vibration || vibreur == null) return;
        try { vibreur.vibrate(motif, -1); } catch (Exception ignore) {}
    }

    // ===============================================================
    // Petits outils
    // ===============================================================
    @Override protected void onPause() {
        super.onPause();
        // interrompue par un appel, une notif, l'écran qui s'éteint :
        // on arrête proprement et on GARDE l'audio déjà capté.
        if (actif) terminer(false);
    }
    @Override protected void onDestroy() { super.onDestroy(); arreter(false); }
    @Override public void onBackPressed() {
        // seul le bouton « Annuler » efface. Un retour par erreur ne me coûte pas ma prise.
        if (actif) terminer(false);
        else if (ecranAccueil.getVisibility() != View.VISIBLE) montrer(ecranAccueil);
        else super.onBackPressed();
    }

    private void montrer(View v) {
        ecranAccueil.setVisibility(v == ecranAccueil ? View.VISIBLE : View.GONE);
        ecranChrono.setVisibility(v == ecranChrono ? View.VISIBLE : View.GONE);
        ecranFini.setVisibility(v == ecranFini ? View.VISIBLE : View.GONE);
        // en revenant à l'accueil, le compteur « en attente » doit être juste
        if (v == ecranAccueil) majEtatPC();
    }

    private static String mmss(int s) {
        if (s < 0) s = 0;
        return (s / 60) + ":" + (s % 60 < 10 ? "0" : "") + (s % 60);
    }

    private static String horodatage() {
        return new java.text.SimpleDateFormat("yyyy-MM-dd_HH'h'mm", java.util.Locale.US)
                .format(new java.util.Date());
    }

    private int dp(int v) { return (int) (v * getResources().getDisplayMetrics().density); }

    private LinearLayout colonne() {
        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.VERTICAL);
        l.setLayoutParams(new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        return l;
    }

    private TextView texte(String s, int taille, int couleur, boolean gras) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextSize(taille);
        t.setTextColor(couleur);
        if (gras) t.setTypeface(t.getTypeface(), android.graphics.Typeface.BOLD);
        return t;
    }

    private TextView centrer(TextView t) { t.setGravity(Gravity.CENTER); return t; }

    private Button grosBouton(String s, int fond, View.OnClickListener clic) {
        Button b = new Button(this);
        b.setText(s);
        b.setTextSize(16);
        b.setTextColor(TEXTE);
        b.setAllCaps(false);
        GradientDrawable g = new GradientDrawable();
        g.setColor(fond);
        g.setCornerRadius(dp(30));
        g.setStroke(dp(1), 0xFF2A3040);
        b.setBackground(g);
        b.setPadding(dp(26), dp(14), dp(26), dp(14));
        b.setOnClickListener(clic);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(10);
        b.setLayoutParams(lp);
        return b;
    }

    private Button petitBouton(String s, View.OnClickListener clic) {
        Button b = new Button(this);
        b.setText(s);
        b.setTextSize(14);
        b.setAllCaps(false);
        b.setPadding(dp(14), dp(8), dp(14), dp(8));
        b.setOnClickListener(clic);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.rightMargin = dp(8);
        b.setLayoutParams(lp);
        return b;
    }

    private void styliserPetit(Button b, boolean allume) {
        GradientDrawable g = new GradientDrawable();
        g.setColor(allume ? 0xFF18241C : CARTE);
        g.setCornerRadius(dp(24));
        g.setStroke(dp(1), allume ? 0xFF2F5A3A : 0xFF2A3040);
        b.setBackground(g);
        b.setTextColor(allume ? TEXTE : GRIS);
    }
}
