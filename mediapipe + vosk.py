import time
import cv2
import mediapipe as mp
import pyaudio
from vosk import Model, KaldiRecognizer
from pynput.mouse import Button
from pynput.mouse import  Controller as mouse_controller
from pynput.keyboard import Controller as keyboard_controller
from threading import Thread, Event
from queue import Queue

model = Model(r"C:\Users\gusta\Documents\vosk\vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16,channels=1,rate=16000,input=True,frames_per_buffer=8192)
stream.start_stream()

mouse = mouse_controller()
keyboard = keyboard_controller()

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

#inicialização de variaveis
# create an event
ordem = [] # ordem dos clicks
record_check = Event() # Evento para checar se a thread principal deve começar a gravar os clicks (True = gravar; False = nao gravar )
send_check = Event() # Evento para cheacar se a lista de comandos deve ser enviada 
limite_pisc = 0.5 #tempo em segundos para considerr uma piscada como voluntária
pisc_controle_d = False
pisc_controle_e = False
piscs_d = 5*[False] # vetor para armazenar os ultimos 3 estados de piscada do olho direito (para evitar que um erro de detecção seja reforçado)
piscs_e = 5*[False] # vetor para armazenar os ultimos 3 estados de piscada do olho esquerdo (para evitar que um erro de detecção seja reforçado)
inicio_d = fim_d = inicio_e = fim_e = 0
vetor_olho_d = [] # vetor para armazenar a distância entre os pontos do olho direito para gerar threshold de piscadas
vetor_olho_e =[] # vetor para armazenar a distância entre os pontos do olho esquerdo para gerar threshold de piscadas
#iniciaçização de funções


def vosk():
    keywords = []
    comando = False
    while True:
        data = stream.read(4096)

        if recognizer.AcceptWaveform(data):
            text = recognizer.Result()
            if text != "":
                if comando == True:
                    
                    keyboard.type(text[14:-3])
                    comando = False
                else:
                    if 'keyboard' in text:
                        comando = True
                    if(text.replace('"','').split()[3]=='start'):
                       #iniciar gravação de novo comando
                       record_check.set()
                    if ((text.replace('"','').split()[3]=='stop') and record_check.is_set()):
                       palavra = text.replace('"','').split()[4]
                       print(palavra, "####")
                       #iniciar gravação de novo comando
                       send_check.set()



def pontos(results):
  #########################################   DISTANCIA ENTRE PONTOS DA BOCA   ##########################################
  db1 = results.multi_face_landmarks[0].landmark[181].y - results.multi_face_landmarks[0].landmark[37].y
  db2 = results.multi_face_landmarks[0].landmark[16].y - results.multi_face_landmarks[0].landmark[0].y
  db3 = results.multi_face_landmarks[0].landmark[314].y - results.multi_face_landmarks[0].landmark[267].y

  db = db1 + db2 + db3

    ####################################### DISTANCIA ENTRE PONTOS DO OLHO DIREITO ###########################################
  der1 = results.multi_face_landmarks[0].landmark[163].y - results.multi_face_landmarks[0].landmark[161].y
  der2 = results.multi_face_landmarks[0].landmark[144].y - results.multi_face_landmarks[0].landmark[160].y
  der3 = results.multi_face_landmarks[0].landmark[145].y - results.multi_face_landmarks[0].landmark[159].y
  der4 = results.multi_face_landmarks[0].landmark[153].y - results.multi_face_landmarks[0].landmark[158].y
  der5 = results.multi_face_landmarks[0].landmark[154].y - results.multi_face_landmarks[0].landmark[157].y

  der6 = results.multi_face_landmarks[0].landmark[163].y -  results.multi_face_landmarks[0].landmark[33].y
  der7 = results.multi_face_landmarks[0].landmark[33].y  - results.multi_face_landmarks[0].landmark[161].y
  der8 = results.multi_face_landmarks[0].landmark[154].y - results.multi_face_landmarks[0].landmark[133].y
  der9 = results.multi_face_landmarks[0].landmark[133].y - results.multi_face_landmarks[0].landmark[157].y

  dd = der1 + der2 + der3 + der4 + der5

    ####################################### DISTANCIA ENTRE PONTOS DO OLHO ESQUERDO ###########################################
  def1 = results.multi_face_landmarks[0].landmark[381].y - results.multi_face_landmarks[0].landmark[384].y
  def2 = results.multi_face_landmarks[0].landmark[380].y - results.multi_face_landmarks[0].landmark[385].y
  def3 = results.multi_face_landmarks[0].landmark[374].y - results.multi_face_landmarks[0].landmark[386].y
  def4 = results.multi_face_landmarks[0].landmark[373].y - results.multi_face_landmarks[0].landmark[387].y

  def5 = results.multi_face_landmarks[0].landmark[277].y - results.multi_face_landmarks[0].landmark[336].y
  def6 = results.multi_face_landmarks[0].landmark[329].y - results.multi_face_landmarks[0].landmark[296].y
  def7 = results.multi_face_landmarks[0].landmark[330].y - results.multi_face_landmarks[0].landmark[334].y
  def8 = results.multi_face_landmarks[0].landmark[280].y - results.multi_face_landmarks[0].landmark[293].y

  de = def1 + def2 + def3 + def4

  return db, dd, de

thread = Thread(target=vosk)
thread.start()

# For webcam input:
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
cap = cv2.VideoCapture(0)
start_time = time.time()
with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image)

    # Draw the face mesh annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_face_landmarks:
        


        if send_check.is_set():
           #print("SALVAR")
           #print(ordem)
           #enviar dados gravados
           send_check.clear()
           record_check.clear()
           #apagando dados gravados
           ordem = []

           
        pos = results.multi_face_landmarks[0].landmark[4]
        db, dd, de = pontos(results)


        if db <0.19:
           #print("boca fechada")
           pos_0 = results.multi_face_landmarks[0].landmark[4]
        else:
          #print("")
          if abs(pos.y -pos_0.y) <= 0.06:
             par_y =  0.5 # parâmetro de deslocamento vertical
          else:
             par_y = 1

          if abs(pos.x -pos_0.x) <= 0.06:
             par_x =  0.5 # parâmetro de deslocamento horizontal
          else:
             par_x = 1

          #print(abs(pos.x -pos_0.x))
          if pos.x > pos_0.x + 0.05:
              #esquerda
              mouse.move(-8 * par_x, 0)  
          elif pos.x < pos_0.x - 0.05: 
              #direita
              mouse.move(8 * par_x, 0)  
          if pos.y > pos_0.y + 0.05:
              #baixo")
              mouse.move(0,8 * par_y) 
          elif pos.y < pos_0.y - 0.05:
              #cima
              mouse.move(0,-8 *par_y)   


        


        if dd<0.025:
            #FECHADO
            pisc_d = True
        else:
            #ABERTO
            pisc_d = False

        for i in range(len(piscs_d)-1):
           piscs_d[i] = piscs_d[i+1]
           piscs_d[-1] = pisc_d

        if piscs_d == [False,False,False,True,True]:
           inicio_d = time.perf_counter()
           pisc_controle_d = True
           #print("INICIO")

        if True in piscs_d:
           fim_d = time.perf_counter()
           #print("FIM")
           
        if (fim_d-inicio_d)>limite_pisc and (pisc_controle_d == True):
          if record_check.is_set():
             ordem.append(('d',mouse.position))
          #print("PISCOU")
          mouse.press(Button.right)
          mouse.release(Button.right)
          pisc_controle_d = False
          
        if de<0.025:
            #FECHADO
            pisc_e = True
        else:
            #ABERTO
            pisc_e = False

        for i in range(len(piscs_e)-1):
           piscs_e[i] = piscs_e[i+1]
           piscs_e[-1] = pisc_e

        if piscs_e == [False,False,False,True,True]:
           inicio_e = time.perf_counter()
           pisc_controle_e = True
           #print("INICIO")

        if True in piscs_e:
           fim_e = time.perf_counter()
           #print("FIM")
           
        if (fim_e-inicio_e)>limite_pisc and (pisc_controle_e == True):
         if record_check.is_set():
            ordem.append(('e',mouse.position))
            #começar a gravar os botoes
            #print("PISCOU")
            mouse.press(Button.left)
            mouse.release(Button.left) 
            pisc_controle_e = False
                 
          
      

    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Face Mesh', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()