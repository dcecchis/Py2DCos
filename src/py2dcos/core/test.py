from twoDspeciesNEW import twoDspecies

file1 = 'C:/Users/julio/OneDrive - Escuela Superior Politécnica del Litoral/Research/Photodegradation of PLA - JoChemEd/Resultados 2DCoS primera prueba/PLA Datos Ordenados.xlsx'

test = twoDspecies(
    filename1=[file1,
               "xlsx",
                0,    # Aquí va el nombre de la hoja correcta del Excel.
                7,         # Fila de inicio (número de fila)
                "A:N",     # Rango de columnas a leer
                True       # Indica si las columnas tienen etiquetas (True o False)
    ],
    reconstruction_comps=0
)
#test.apply_node_attenuation(a=1, lam=1, eps=1e-7)
test.syn(method='HT')
test.asyn(method='HT')
test.plotFunction(
    corrType='homo', calcMethod='HT', refSpectra='ini', colorMap='coolwarm',
    numOfContour=6, locator_choice='asinh', syncDiag='main', asyncDiag='main', xAxis='decreasing', colorMapIntensity=1.0,
    colorLines='black', colorLinesIntensity=0.6, shownGraph='async', canvas=False, figure=None,
                     eqSpaced=True, peaks_signs='all'
)
