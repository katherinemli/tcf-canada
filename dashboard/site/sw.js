// ============================================================
// Service worker : c'est lui qui rend l'app utilisable HORS LIGNE.
//
// À la première visite, il garde une copie des fichiers. Ensuite,
// l'app s'ouvre même sans réseau : dans le métro, en avion, ou
// quand on ne veut surtout pas dépendre du wifi du bureau.
//
// Après avoir modifié index.html, changer le numéro de VERSION :
// c'est ce qui dit au téléphone d'aller chercher la nouvelle copie.
// ============================================================

const VERSION = "tcf-oral-v1";
const FICHIERS = [
  "./", "./index.html", "./manifest.webmanifest",
  "./icone-180.png", "./icone-192.png", "./icone-512.png",
];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(VERSION)
      // addAll échoue en bloc si un seul fichier manque : on les ajoute
      // un par un pour qu'une icône absente ne casse pas l'installation.
      .then(c => Promise.all(FICHIERS.map(f => c.add(f).catch(() => {}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(noms => Promise.all(noms.filter(n => n !== VERSION).map(n => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  // On sert la copie tout de suite (rapide, marche hors ligne) et on
  // rafraîchit en arrière-plan pour la prochaine ouverture.
  e.respondWith(
    caches.match(e.request).then(copie => {
      const reseau = fetch(e.request).then(rep => {
        if (rep && rep.status === 200 && rep.type === "basic") {
          const clone = rep.clone();
          caches.open(VERSION).then(c => c.put(e.request, clone));
        }
        return rep;
      }).catch(() => copie);
      return copie || reseau;
    })
  );
});
