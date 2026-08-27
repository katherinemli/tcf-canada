#!/bin/bash
# Fabrique TCF-Oral.apk — sans Gradle, sans Android Studio.
# Il suffit de : bash construire.sh
set -e
cd "$(dirname "$0")"

SDK=~/android-min
BT=$SDK/android-13            # build-tools 33.0.2
JAR=$SDK/android-9/android.jar # API 28 = Android 9, comme le Honor 9
OUT=build

rm -rf $OUT && mkdir -p $OUT/gen $OUT/classes $OUT/res

echo "1/6  ressources…"
$BT/aapt2 compile --dir res -o $OUT/res.zip

echo "2/6  manifeste…"
$BT/aapt2 link -o $OUT/base.apk -I $JAR \
    --manifest AndroidManifest.xml \
    --java $OUT/gen \
    --min-sdk-version 21 --target-sdk-version 28 \
    $OUT/res.zip

echo "3/6  java…"
javac -nowarn -Xlint:-options -source 8 -target 8 -bootclasspath $JAR \
    -d $OUT/classes $(find src $OUT/gen -name '*.java')

echo "4/6  dex…"
$BT/d8 --release --min-api 21 --lib $JAR --output $OUT \
    $(find $OUT/classes -name '*.class')

echo "5/6  assemblage…"
python3 - <<'PY'
import zipfile, shutil
shutil.copy("build/base.apk", "build/avec-dex.apk")
with zipfile.ZipFile("build/avec-dex.apk", "a", zipfile.ZIP_DEFLATED) as z:
    z.write("build/classes.dex", "classes.dex")
PY
$BT/zipalign -f 4 $OUT/avec-dex.apk $OUT/aligne.apk

echo "6/6  signature…"
if [ ! -f cle.keystore ]; then
    keytool -genkeypair -keystore cle.keystore -alias tcf \
        -storepass android -keypass android -keyalg RSA -keysize 2048 \
        -validity 10000 -dname "CN=TCF Oral, O=Katherine, C=CL" >/dev/null 2>&1
fi
$BT/apksigner sign --ks cle.keystore --ks-pass pass:android --key-pass pass:android \
    --out TCF-Oral.apk $OUT/aligne.apk

$BT/apksigner verify TCF-Oral.apk && echo
echo "✅  TCF-Oral.apk prêt  ($(du -h TCF-Oral.apk | cut -f1))"
