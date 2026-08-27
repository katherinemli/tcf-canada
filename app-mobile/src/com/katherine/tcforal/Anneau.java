package com.katherine.tcforal;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.RectF;
import android.view.View;

/** L'anneau qui se remplit pendant que je parle. */
public class Anneau extends View {

    private final Paint piste = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint jauge = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF cadre = new RectF();
    private float part = 0f;

    public Anneau(Context c) {
        super(c);
        piste.setStyle(Paint.Style.STROKE);
        piste.setColor(0xFF222836);
        jauge.setStyle(Paint.Style.STROKE);
        jauge.setColor(0xFF4FD1C5);
        jauge.setStrokeCap(Paint.Cap.ROUND);
    }

    /** part = 0 au début, 1 à la fin. */
    public void regler(float p, int couleur) {
        part = p < 0 ? 0 : (p > 1 ? 1 : p);
        jauge.setColor(couleur);
        invalidate();
    }

    @Override
    protected void onDraw(Canvas c) {
        float ep = getWidth() * 0.055f;
        piste.setStrokeWidth(ep);
        jauge.setStrokeWidth(ep);
        float m = ep / 2f + 2;
        cadre.set(m, m, getWidth() - m, getHeight() - m);
        c.drawArc(cadre, 0, 360, false, piste);
        c.drawArc(cadre, -90, 360 * part, false, jauge);
    }
}
