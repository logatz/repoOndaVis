# -*- coding: utf-8 -*-

#%% Carregar bibliotecas
import os
#import datetime as dt
#import time
from datetime import date, timedelta
import xarray
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import pandas as pd

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

#%% Atualziar o arquio com parametros para o CEMEMS
diretorio = os.getcwd()

## Atualziza data de interesse e local do arq saida
diaini = 'date_min=' + str(date.today()) + '\n'
diafim = 'date_max=' + str(date.today() + timedelta(days=5)) + '\n'
dirSaida = 'out_dir=' + diretorio + '\n'

## Acessa arquivo
Arquivo = open(os.path.join(diretorio, 'arqConfig.ini'))

## lista as linhas do arquivo e fecha o arquivo
linhas = Arquivo.readlines()
Arquivo.close()
#print(linhas)
## Atualiza as linhas das datas
linhas[9] = diaini
linhas[10] = diafim
linhas[21] = dirSaida
##Abre e atualzia o arquivo com as novas datas
Arquivo = open(os.path.join(diretorio, 'arqConfig.ini'), 'w')
novoConteudo = "".join(linhas)
Arquivo.write(novoConteudo)
Arquivo.close()

### Verifica se o arquivo esta ok (Apenas para desenvolver, manter comentado)
#lerArquivo = open(os.path.join(diretorio, 'arqConfig.ini'))
#verArquivoLido = lerArquivo.read()
#print(verArquivoLido)


#%% chama o Motuclient com base no arquivo parametrizado

caminhoMotu = os.path.join(diretorio, 'motu\src\motuclient\motuclient.py --config-file arqConfig.ini')
os.system('python ' + caminhoMotu)

## Exemplo linha de comando para ser usada diretamente no terminal
## python -m motuclient --motu https://nrt.cmems-du.eu/motu-web/Motu --service-id GLOBAL_ANALYSIS_FORECAST_WAV_001_027-TDS --product-id global-analysis-forecast-wav-001-027 --longitude-min -53.3695 --longitude-max -36 --latitude-min -33.7445 --latitude-max -22.5 --date-min "2022-02-15 00:00:00" --date-max "2022-02-16 00:00:00" --variable VHM0 --variable VHM0_WW --variable VMDR --variable VMDR_WW --variable VPED --out-dir 'D:\Dropbox\XGarbossa\Epagri\Servicos\0_Finalizados\2020-12-DadosCMENS_siteCiram' --out-name 'teste.nc' --user 'lhpgarbossa' --pwd '8z9vx$tMmR'


#%% Acessar os dados do NC baixado
arquivoNC = xarray.open_dataset(os.path.join(diretorio,'ondasDoCMEMS.nc'))
### Separa os dados de interesse , sendo por enquanto: sea_surface_wave_significant_height (SWH) = VHM0
###                                                    sea surface wave from direction (vmdr) = VMDR
ondaAlt = arquivoNC['VHM0']
ondaDir = arquivoNC['VMDR']
tempo = ondaAlt['time'].values

# Gera a grade numérica baseado na Lat/Lon dos dados do CMEMS
lon, lat = np.meshgrid(ondaAlt['longitude'][:].values, ondaAlt['latitude'][:].values)
### Converte de Nan para 0 os dados de altura de mare para facilitar interpolação próximo das margens
ondaAltZeros = np.nan_to_num(ondaAlt)


## Funcao converter graus em componentes ortogonais dos vetores U e V
def Dir2UV(Dir):
    U = -10 * np.sin(Dir * (np.pi/180))
    V = -10 * np.cos(Dir * (np.pi/180))
    return U, V
## Vetorizar a funcao facilita o uso dos dados poie eles saem como um Array de dados
## Se usar a função acima sem vetorizar, vc obtem como resultado um Objeto de dataArray do Xarray, mais dificil de manipular 
Dir2UV = np.vectorize(Dir2UV)

U, V = Dir2UV(ondaDir)

#%%  Passo de tempo para rodar todas as imagens
i=0
for t in tempo:
    horaOnda = (pd.to_datetime(str(t))).strftime('%d/%m/%Y %H:%M')

#%%
##    print(horaOnda)

    fig = plt.figure(figsize=(16,12))  # cria figura
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.axis('off')
    
    #Availar se usa shape ou usa alguma alternativa de banco de dados da internet
    lerEstados = shapereader.Reader(r'E:\WAVES\BR\Brasil.shp')
#    lerMunicipios = shapereader.Reader(r'D:\Dropbox\XGarbossa\Epagri\Pesquisas\2022-UFPR-OLEO\Temperatura_Rios\SC\SC.shp')
    estados = list(lerEstados.geometries())
#    municipios = list(lerMunicipios.geometries())
    contornoEstados = cfeature.ShapelyFeature(estados, ccrs.PlateCarree())
#    contornoMunicipios = cfeature.ShapelyFeature(municipios, ccrs.PlateCarree())
    ax.add_feature(contornoEstados, facecolor='w',linewidth=0.5, edgecolor='black', zorder=97)
    #ax.add_feature(contornoMunicipios, facecolor='none',linewidth=0.75, edgecolor='white', alpha=0.5, zorder=96)
    
    import matplotlib.colors as colors    # para usar ormalziacao nas imagens
    ### Na normalização se usar gamma=1 é a mesma coisa que não fazer normalziação
    
    ## Extrai os dados de interessse
    #Teste = np.squeeze(ondaAlt[2,:])
    #Teste2 = np.nan_to_num(Teste)
    
    intervalosDHN = [0, 1, 1.5, 2, 2.5, 3, 3.5, 4, 6, 7]
    intervaloContorno = [1.5, 2, 2.5, 3, 3.5, 4, 6, 7]
    #intervalos = [1, 2, 3, 4, 5, 6]
    #etiqueta = ["susse", "opa", "Cara!!", "Não vai!", "Quer morrer???", "Vc tem um trasnatlantico?"]

#    SUAVE = plt.pcolormesh(lon, lat, ondaAltZeros[i,:], transform=ccrs.PlateCarree(), cmap=get_cmap("RdYlBu_r"),vmin=0 ,vmax=14, norm = colors.PowerNorm(gamma=0.5), zorder=94)
    
    W = plt.contourf(lon, lat, ondaAltZeros[i,:],levels=intervalosDHN, transform=ccrs.PlateCarree(), cmap=get_cmap("RdYlBu_r"), extend='max', norm = colors.PowerNorm(gamma=0.7), zorder=93)
    X = plt.contour(lon, lat, ondaAltZeros[i,:],levels=intervaloContorno, transform=ccrs.PlateCarree(), colors=['black'], linewidths = 0.5, linestyles = 'dashed', zorder=94)
    plt.clabel(X, inline=True, fontsize=16, fmt=' {:.2f} '.format, colors=['r'])
   
    ### extend= pode ser min, max ou both
    # controle barra de cores
    #cbar=plt.colorbar(ax=ax, shrink=.50, pad=0.05, orientation='horizontal', ticks=intervalos,  aspect=50)
    cbar=plt.colorbar(W, shrink=.50, pad=0.05, orientation='horizontal', aspect=40)
    cbar.set_label("Altura significativa de ondas [m]", fontsize=14)
    #cbar.set_ticklabels(etiqueta)
    cbar.ax.tick_params(labelsize=14)
    
    Dm = 4
    Q = plt.quiver(lon[::Dm, ::Dm], lat[::Dm, ::Dm], U[i, ::Dm, ::Dm], V[i, ::Dm, ::Dm], color='gray', pivot='mid', units='inches', scale=65, width=0.07, minshaft = 2, minlength=0, zorder=95)
    ### Quiver opt. --> scale , for smaller values == longer arrows
    ###     --> pivot{'tail', 'mid', 'middle', 'tip'}, default: 'tail' The part of the arrow that is anchored to the X, Y grid
    ###     --> color is a color or a color sequence (optional) 
    ###     --> The arrow dimensions (except for length) are measured in multiples of this unit. Ex.: 'dots', 'inches': Pixels or inches based on the figure dpi.
    ###     --> width is the shaft width based on arrow units
    
    ## Titulo da imagem
    ax.set_title(f'SWH - {horaOnda}GMT', fontsize=16, fontname='Ubuntu')
    
    # Define limites do mapa
    #ax.set_xlim(cartopy_xlim(temp))
    #ax.set_ylim(cartopy_ylim(temp))
    ax.set_extent([-53, -45, -32.1, -22.9], ccrs.PlateCarree()) ## para Dominio 1
    #ax.set_extent([-50, -47, -29.0, -25.0], ccrs.PlateCarree()) ## para Dominio 2
    
    #trabalha com as linhas de grade
    gl = ax.gridlines(ccrs.PlateCarree(), draw_labels=True, x_inline=False, y_inline=False, linewidth=1, color='gray', alpha=0.5, zorder=98, linestyle='--')
    gl.top_labels = False # ver 0.2 do matplolib
##  gl.xlabels_top = None # ver 0.17 do matplolib
    gl.bottom_labels = True
    gl.right_labels = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 22, 'color': 'gray', }
    gl.xlabel_style = {'color': 'black', 'weight': 'normal'}
    gl.ylabel_style = {'size': 22, 'color': 'gray'}
    gl.ylabel_style = {'color': 'black', 'weight': 'normal'}
    
    #adiciona pontos de referencia
    cidades=np.array([[-23.96, -48.00, "SÃO PAULO"],
                      [-25.00, -51.00, "PARANÁ"],
                      [-25.54, -48.30, "Ilha do Mel"],
                      [-27.50, -51.50, "SANTA CATARINA"],
                      [-26.22, -48.46, "Ilha da Paz"],
                      [-26.907, -48.661, "Itajaí"],
                      [-27.59, -48.54, "Florianópolis"],
                      [-28.50, -48.80, "Laguna"],
                      [-29.98, -53.00, "RIO GRANDE DO SUL"],
                      [-29.35, -49.70, "Torres"],
                      [-31.00, -50.92, "Mostardas"],
                      [-32.00, -52.00, "Rio Grande"]])
    
    for c in range(len(cidades)):
        plt.plot(cidades[c,1].astype(float), cidades[c,0].astype(float),  marker=11, markersize=5, color="black", transform=ccrs.PlateCarree(), zorder = 99)
        plt.text(cidades[c,1].astype(float)+0.2, cidades[c,0].astype(float)+0.0, cidades[c,2].astype(str), fontsize=13, fontweight='normal',
                 horizontalalignment = 'left', verticalalignment = 'baseline', color='black', transform=ccrs.PlateCarree(), zorder = 99)

    plt.savefig(diretorio + '\wav-'+ str(i) + '.png', format='png', dpi=96, bbox_inches='tight')    
    plt.close()   ## pode usar para fechar as janelas apos salvar a figura e evitar consumo de memoria

#%%    
    i = i+1

#%%
import PIL
Dt = list(range(1, len(list(tempo))))

image_frames = []
i = 0
for i in Dt:
##    i = 't{:05d}'.format(i)
##    novoframe = PIL.Image.open(diretorio + '\wav-'+ str(i) + '.png')
    novoframe = PIL.Image.open(diretorio + '\wav-'+ str(i) + '.png')
    image_frames.append(novoframe)

image_frames[0].save(diretorio + '\W_' + str(date.today()) + '.gif', format = 'GIF', 
                     append_images = image_frames[1: ], save_all = True, duration = 1000, loop = 0)
