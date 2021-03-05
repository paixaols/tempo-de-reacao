# -*- coding: utf-8 -*-
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import tkinter as tk

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.frame_objeto = tk.Frame(self, borderwidth = 1, relief = 'groove')
        self.frame_objeto.pack(side = 'left', fill = 'y', expand = True)
        
        self.frame_grafico = tk.Frame(self, borderwidth = 1, relief = 'groove')
        self.frame_grafico.pack(side = 'right')
        
        self.init_frame_objeto()
        self.init_frame_grafico()
        
        self.tempo_start = []# Tempo em que o usuário aciona o 
        self.tempo_stop = [] # cronômetro (relativo ao início da queda)
        self.tempo_queda = []# Tempo de queda da bolinha
        self.estado = 'parado'
        self.clock = 10# ms
        self.g = 0.15
    
    def init_frame_objeto(self):
        self.countdown = tk.IntVar()
        self.countdown.set(0)
        tk.Label(self.frame_objeto, textvariable = self.countdown, 
                 font = ('arial', 20)).pack(padx = 10, pady = 10)
        
        self.botao_cronometro = tk.Button(self.frame_objeto, text = 'Pronto!', 
                                          width = 10, command = self.b_press)
        self.botao_cronometro.pack(pady = 5)
        
        self.largura, self.altura = (450, 350)
        self.canvas_obj = tk.Canvas(self.frame_objeto, height = self.altura, 
                                    width = self.largura, bg = 'darkgray')
        self.canvas_obj.pack()
        
        tk.Label(self.frame_objeto, text = 'Repetições:').pack(pady = 5)
        self.num_repet = tk.IntVar()
        self.num_repet.set(0)
        tk.Label(self.frame_objeto, 
                 textvariable = self.num_repet).pack(pady = 5)
        
        self.desenhar_bolinha()
    
    def init_frame_grafico(self):
        tk.Button(self.frame_grafico, text = 'Exportar', width = 10, 
                  command = self.exportar).pack(pady = 5)
        
        fig = Figure(figsize = (8, 5), dpi = 100)
        self.ax = fig.add_subplot(111)
        
        self.canvas_graf = FigureCanvasTkAgg(fig, self.frame_grafico)
        self.canvas_graf.get_tk_widget().pack()
    
    def exportar(self):
        with open('output.txt', 'w') as f:
            f.write('Start (s)\tStop (s)\tt queda (s)\n')
            for i in range(len(self.tempo_start)):
                f.write('{}\t{}\t{}\n'.format(self.tempo_start[i], 
                                              self.tempo_stop[i], 
                                              self.tempo_queda[i]))
    
    def b_press(self):
        if self.estado == 'parado':
            self.estado = 'contagem'
            self.botao_cronometro.configure(text = 'Start')
            self.iniciar_simulacao()
            self.after(1000, self.contagem)
        elif self.estado == 'contagem':
            self.estado = 'simulando'
            self.botao_cronometro.configure(text = 'Stop')
            self.t_start_usuario = time.time()
        elif self.estado == 'simulando':
            self.estado = 'parado'
            self.botao_cronometro.configure(text = 'Pronto!')
            self.t_stop_usuario = time.time()
    
    def contagem(self):
        t = self.countdown.get()-1
        self.countdown.set(t)
        if t == 0:
            self.t_start = time.time()
            self.run()# Simular o movimento da bolinha
        else:
            self.after(1000, self.contagem)
    
    def desenhar_bolinha(self):
        x = self.largura/2
        self.y = 50
        self.vy = 0
        self.raio = 10
        self.canvas_obj.delete('esfera')
        self.canvas_obj.create_oval(x-self.raio, self.y-self.raio, 
                                    x+self.raio, self.y+self.raio, 
                                    fill = 'red', tags = 'esfera')
    
    def iniciar_simulacao(self):
        self.desenhar_bolinha()
        self.countdown.set(3)
        
        # Os tempos abaixo são timestamps.
        self.t_start = 0# Início real
        self.t_stop = 0 # e fim real da queda
        self.t_start_usuario = 0# Usuário inicia
        self.t_stop_usuario = 0 # e para o cronômetro.
    
    def run(self):
        vel_pos_quique = 0.4# Multiplicador da velocidade anterior.
        if self.y > self.altura-self.raio:
            self.vy = -abs(self.vy)*vel_pos_quique
            if self.t_stop == 0:
                self.t_stop = time.time()
        else:
            self.vy += self.g
        self.y += self.vy
    
        self.canvas_obj.move('esfera', 0, self.vy)
        tempo = time.time()
        if tempo-self.t_start < 2:# 2s é o tempo máximo de simulação.
            self.after(self.clock, self.run)
        else:
            self.plot()
    
    def plot(self):
        self.num_repet.set(self.num_repet.get()+1)
        
        self.tempo_start.append(self.t_start_usuario-self.t_start)
        self.tempo_stop.append(self.t_stop_usuario-self.t_start)
        self.tempo_queda.append(self.t_stop-self.t_start)
        
        self.ax.clear()
        self.ax.hist(self.tempo_start, color = '#0080e0')
        self.ax.hist(self.tempo_stop, color = '#ff5900')
        self.ax.axvline(0, ls = '--', color = '#004478')
        self.ax.axvline(self.t_stop-self.t_start, ls = '--', color = '#b33e00')
        
        self.ax.set_xlabel('Tempo (s)')
        self.canvas_graf.draw()

app = Application()
app.resizable(False, False)
app.bind_all('<Escape>', lambda event: app.destroy())
app.mainloop()
