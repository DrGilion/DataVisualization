#!/bin/sh

OF=/tmp/vis_data.zip
OD=/tmp/
OD_FN=vis_data
CURL_COOKIE=/tmp/curl_cookie
G_FILEID="13_mpXqvANs20WZBKDG76rtiZtcg-xbl3"

# cleanup in advance
rm -f ${OF}
rm -f ${CURL_COOKIE}
rm -rf ${OD}/${OD_FN}


curl -c ${CURL_COOKIE} -s -L "https://drive.google.com/uc?export=download&id=${G_FILEID}" > /dev/null
curl -Lb ${CURL_COOKIE} "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ${CURL_COOKIE}`&id=${G_FILEID}" -o ${OF}

unzip ${OF} -d ${OD}

rm -f ${OF}
rm -f ${CURL_COOKIE}
