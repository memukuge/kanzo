# kanzo - notepad with a stenographer

## はじめに
このアプリケーションは、選択したPCのマイク入力の音声をリアルタイムに文字起こしする機能を備えたメモ帳です。
認識が行われたその場で修正を進めることができ、効率的な発言録の作成や、ウェブ会議における聞き取り補助に利用できます。

## 使い方
Releaseページからwindows 64bit向けのビルド済みリリースをダウンロードして解凍し、
ディレクトリ内のkanzo.exeを実行してください。

* modelタブでは、音声認識に使う、vosk言語認識モデルを選択できます。
デフォルトでは日本語だけですが、アプリケーションディレクトリ内modelsディレクトリに、ほかのvosk音声モデルを格納することで
他の言語の文字起こしも行えます。モデルは以下からDLしてください。
https://alphacephei.com/vosk/models

* deviceタブでは、聞き取りを行う音声入力デバイスを選択できます。
windowsサウンドミキサーや、音声ループバックデバイス作成アプリ（VB-Audio Virtual Cableなど　https://vb-audio.com/Cable/ )
を使って、PCで再生される音声を入力にループバックすることで、ウェブ会議等の相手の音声を入力することができます。

* そのほか、fontタブでは文字の大きさを設定できるほか、otherタブでウィンドウの常時表示、オートスクロール、テキスト保存の設定ができます。

## ソースコードからの起動
ソースコードをクローンして、お好きなpython環境で実行してください。以下のパッケージをあらかじめインストールする必要があります。
sounddevice(0.4.4)、vosk、ktinker、numpy
なお、tag 0.2betaに当たるコードからは、portaudioのwasapi loopbackパッチ版を使っています。
https://github.com/memukuge/portaudiobinary_wasapi

