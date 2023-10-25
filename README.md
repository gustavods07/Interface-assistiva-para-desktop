# Interface assistiva para Desktop
Projeto de inteface para interação entre pessoas tetraplégicas e computadores pessoais. Ao executar o script _mediapipe + vosk.py_,  o cursor do computador passa a ser controlado por gestos faciais através da captura de imagens do rosto em conjunto com a biblioteca _Mediapipe_. Além disso, através da biblioteca _Vosk_, o usuário pode utilizar transcrição de voz para digitar ou automatizar uma rotina de clicks. 


O script monitora:
- a posição relativa do nariz em relação ao ponto inicial (mapeado com base na ultima localização anterior à abertura da boca do usuário),
- a abertura dos olhos, transformando piscadas em cliks,
- as palavras pronunciadas pelo usuário, para transcrição em texto ou automatização de rotinas de clicks.


# Movimentação do cursor

A movimentação do cursor baseia-se na abertura da boca como ação-gatilho. Dessa forma, ao abrir a boca e girar o rosto parcialmente (para qualquer dos lados ou para cima), o cursor se movimenta pela tela. Quanto maior on ângulo do giro facial, maior a valocidade do cursor.


# Clicks

Os clicks são computados através de piscadas. há um limite temporal (duração de piscadas intencionais deve ser superior a 0.3 segundos) para  diferenciar piscadas involuntárias de piscadas intencionais. Os clicks podem ser descritos da seguinte forma:
- piscar o olho direito é interpretado como click com o botão direito de um mouse;
- piscar o olho esquerdo é interpretado como click com o botão esquerdo de um mouse.

# Transcrição de áudio para digitação




