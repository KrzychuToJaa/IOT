import json,shutil,io,contextlib,base64,os,sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path.cwd();path=root/'Zadanie 3/Zadanie_3__IoT.ipynb';qa=root/'.tmp_report/zadanie3';qa.mkdir(parents=True,exist_ok=True)
shutil.copy2(path,qa/'Zadanie_3_przed_uproszczeniem.ipynb')
original=json.loads(path.read_text(encoding='utf-8'))
cells=[]
def md(text):cells.append({'cell_type':'markdown','metadata':{},'source':text.splitlines(keepends=True)})
def code(text):cells.append({'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':text.splitlines(keepends=True)})
md('''# Analiza jakości powietrza
Krzysztof Kata 254776  
Zadanie 3

Celem zadania jest analiza stężenia CO i prosta prognoza na kolejne 7 dni.

Źródło: [Air Quality — UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/360/air+quality), S. Vito, 2008, DOI: 10.24432/C59K5F.
Zbiór zawiera pomiary układu czujników gazu oraz analizatora referencyjnego.
Analizowana kolumna CO(GT) podaje stężenie CO z analizatora w mg/m³.
Wartość -200 oznacza brak pomiaru.
''')
code('''from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

plik = "AirQualityUCI.zip"
if not Path(plik).exists():
    urlretrieve("https://archive.ics.uci.edu/static/public/360/air+quality.zip", plik)

with ZipFile(plik) as archiwum:
    dane = pd.read_csv(archiwum.open("AirQualityUCI.csv"),
                       sep=";", decimal=",", na_values=-200)
dane = dane.dropna(subset=["Date", "Time"])
dane.index = pd.to_datetime(dane["Date"] + " " + dane["Time"],
                            format="%d/%m/%Y %H.%M.%S")
dane = dane.sort_index()
co = dane["CO(GT)"].resample("D").mean()
''')
md('''## Analiza danych
Statystyki dotyczą pomiarów godzinowych. Wykres pokazuje średnie dzienne z dostępnych pomiarów. Dni bez odczytów pozostają puste.
''')
code('''print("Liczba pomiarów:", len(dane))
print("Braki CO:", dane["CO(GT)"].isna().sum())
print(dane["CO(GT)"].agg(["mean", "min", "max"]).round(3))

co.plot(figsize=(10, 3), title="Średnie dzienne stężenie CO", grid=True)
plt.xlabel("Data")
plt.ylabel("CO [mg/m³]")
plt.tight_layout()
plt.show()
''')
md('''## Prognoza na 7 dni
Regresja liniowa przewiduje CO na podstawie numeru dnia. Używam ostatnich 30 dni, aby opisać ostatni trend. Pomijam dni bez pomiarów. Najpierw uczę model na wcześniejszych dniach i sprawdzam go na ostatnich 7 dniach. MAE to średni błąd w mg/m³. Następnie uczę model na całym tym okresie i prognozuję tydzień po końcu zbioru.
''')
code('''ostatnie = co.loc[co.index >= co.index[-1] - pd.Timedelta(days=29)].dropna()
x = (ostatnie.index - ostatnie.index[0]).days.to_numpy().reshape(-1, 1)

model = LinearRegression()
model.fit(x[:-7], ostatnie.iloc[:-7])
blad = mean_absolute_error(ostatnie.iloc[-7:], model.predict(x[-7:]))
print(f"MAE na ostatnich 7 dniach: {blad:.2f} mg/m³")

model.fit(x, ostatnie)
print(f"Trend ostatnich 30 dni: {model.coef_[0]:+.4f} mg/m³ na dobę")
daty = pd.date_range(co.index[-1] + pd.Timedelta(days=1), periods=7)
x_prognozy = (daty - ostatnie.index[0]).days.to_numpy().reshape(-1, 1)
prognoza = pd.Series(model.predict(x_prognozy), index=daty)
print(prognoza.round(2).rename("Prognoza CO [mg/m³]"))

ostatnie.plot(figsize=(10, 3), label="Pomiary", grid=True)
pd.concat([ostatnie.iloc[-1:], prognoza]).plot(label="Prognoza", style="--o")
plt.title("Stężenie CO i prognoza na 7 dni")
plt.xlabel("Data")
plt.ylabel("CO [mg/m³]")
plt.legend()
plt.tight_layout()
plt.show()
''')
md('''## Wnioski
Średnie stężenie CO wyniosło 2,153 mg/m³, minimum 0,1 mg/m³, a maksimum 11,9 mg/m³.
Trend ostatnich 30 dni wyniósł około -0,0137 mg/m³ na dobę. Model przewiduje niewielki spadek stężenia od 1,73 do 1,65 mg/m³ w dniach 5–11 kwietnia 2005 r.

MAE wyniosło 0,75 mg/m³, więc prognoza jest orientacyjna i nie oddaje nagłych zmian.
W systemie IoT taki wynik może wspomagać planowanie częstszych pomiarów lub ostrzeżeń przy przewidywanym wzroście CO. Decyzje powinny uwzględniać również bieżące odczyty czujników.
''')
# Execute the actual notebook cells in order, saving real outputs and plots.
os.chdir(root/'Zadanie 3');env={'__name__':'__main__'};count=0
for cell in cells:
 if cell['cell_type']!='code':continue
 count+=1;cell['execution_count']=count
 stream=io.StringIO();out=cell['outputs']
 def show(*args,**kwargs):
  text=stream.getvalue()
  if text:out.append({'output_type':'stream','name':'stdout','text':text.splitlines(keepends=True)});stream.seek(0);stream.truncate(0)
  for num in plt.get_fignums():
   fig=plt.figure(num);buf=io.BytesIO();fig.savefig(buf,format='png',dpi=120)
   png=buf.getvalue();(qa/f'wykres_{count}.png').write_bytes(png)
   out.append({'output_type':'display_data','metadata':{},'data':{'image/png':base64.b64encode(png).decode(),'text/plain':['<Figure>']}})
  plt.close('all')
 env['plt']=plt;plt.show=show
 with contextlib.redirect_stdout(stream):exec(compile(''.join(cell['source']),f'cell_{count}','exec'),env)
 if stream.getvalue():out.append({'output_type':'stream','name':'stdout','text':stream.getvalue().splitlines(keepends=True)})
notebook={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':sys.version.split()[0]}},'nbformat':4,'nbformat_minor':5}
for i,c in enumerate(cells):c['id']=f'zadanie3-{i+1}'
path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
print('Zapisano i wykonano:',path)
for c in cells:
 for o in c.get('outputs',[]):
  if o['output_type']=='stream':print(''.join(o['text']))
print('Komórki:',len(cells),'Wykresy:',len(list(qa.glob('wykres_*.png'))))
