# Interface assistiva para Desktop
Projeto de inteface para interação entre pessoas tetraplégicas e computadores pessoais. Ao executar o script _mediapipe + vosk.py_ o cursor do computador passa a ser controlado por movimentos e gestos faciais através da biblioteca _Mediapipe_. Além disso, através da biblioteca _Vosk_, o usuário pode utilizar transcrição de voz para digitar ou automatizar uma rotina de clicks. 


O script monitora:
- a posição relativa do nariz em relação ao ponto inicial (mapeado com base na ultima localização anterior à abertura da boca do usuário),
- a abertura dos olhos, transformando piscadas em cliks,
- as palavras pronunciadas pelo usuário, para transcrição em texto ou automatização de rotinas de clicks.

- 


