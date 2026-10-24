import json,io,contextlib,base64,os,sys,shutil
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.stdout.reconfigure(encoding='utf-8')
root=Path.cwd();p=root/'Zadanie 3/Zadanie_3__IoT.ipynb';qa=root/'.tmp_report/zadanie3';qa.mkdir(parents=True,exist_ok=True)
shutil.copy2(p,qa/'Zadanie_3_przed_dniem_tygodnia.ipynb')
n=json.loads(p.read_text(encoding='utf-8'))
n['cells'][4]['source']='''## Prognoza na 7 dni
Regresja liniowa uwzględnia trend czasowy i dzień tygodnia. Każdy dzień ma osobną cechę 0/1, a niedziela jest punktem odniesienia. Dzięki temu model może przewidywać inne stężenia np. w poniedziałek i w sobotę.

Używam ostatnich 30 dni i pomijam dni bez pomiarów. Ostatnie 7 dni służy do sprawdzenia modelu. MAE to średni błąd w mg/m³. Następnie uczę model na całym tym okresie i prognozuję kolejny tydzień.
'''.splitlines(keepends=True)
n['cells'][5]['source']='''ostatnie = co.loc[co.index >= co.index[-1] - pd.Timedelta(days=29)].dropna()

def cechy(daty):
    x = pd.DataFrame({"trend": (daty - ostatnie.index[0]).days}, index=daty)
    for dzien in range(6):
        x[f"dzien_{dzien}"] = (daty.dayofweek == dzien).astype(int)
    return x

x = cechy(ostatnie.index)
model = LinearRegression()
model.fit(x.iloc[:-7], ostatnie.iloc[:-7])
blad = mean_absolute_error(ostatnie.iloc[-7:], model.predict(x.iloc[-7:]))
print(f"MAE na ostatnich 7 dniach: {blad:.2f} mg/m³")

model.fit(x, ostatnie)
print(f"Trend po uwzględnieniu dnia tygodnia: {model.coef_[0]:+.4f} mg/m³ na dobę")
daty = pd.date_range(co.index[-1] + pd.Timedelta(days=1), periods=7)
prognoza = pd.Series(model.predict(cechy(daty)), index=daty)
nazwy = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Niedz"]
print(pd.DataFrame({"Dzień": [nazwy[d] for d in daty.dayofweek],
                    "Prognoza CO [mg/m³]": prognoza.round(2)}))

ostatnie.plot(figsize=(10, 3), label="Pomiary", grid=True)
pd.concat([ostatnie.iloc[-1:], prognoza]).plot(label="Prognoza", style="--o")
plt.title("Prognoza CO z uwzględnieniem dnia tygodnia")
plt.xlabel("Data")
plt.ylabel("CO [mg/m³]")
plt.legend()
plt.tight_layout()
plt.show()
'''.splitlines(keepends=True)
os.chdir(root/'Zadanie 3');env={'__name__':'__main__'};count=0
for c in n['cells']:
 if c['cell_type']!='code':continue
 count+=1;c['execution_count']=count;c['outputs']=[];stream=io.StringIO();out=c['outputs']
 def show(*args,**kwargs):
  if stream.getvalue():out.append({'output_type':'stream','name':'stdout','text':stream.getvalue().splitlines(keepends=True)});stream.seek(0);stream.truncate(0)
  for num in plt.get_fignums():
   buf=io.BytesIO();plt.figure(num).savefig(buf,format='png',dpi=120);png=buf.getvalue()
   (qa/f'dzien_tygodnia_{count}.png').write_bytes(png)
   out.append({'output_type':'display_data','metadata':{},'data':{'image/png':base64.b64encode(png).decode(),'text/plain':['<Figure>']}})
  plt.close('all')
 plt.show=show
 with contextlib.redirect_stdout(stream):exec(compile(''.join(c['source']),f'cell_{count}','exec'),env)
 if stream.getvalue():out.append({'output_type':'stream','name':'stdout','text':stream.getvalue().splitlines(keepends=True)})
prog=env['prognoza'];trend=env['model'].coef_[0];mae=env['blad']
print('MAE:',mae,'Trend:',trend);print(prog)
conclusion=f'''## Wnioski
Średnie stężenie CO wyniosło 2,153 mg/m³, minimum 0,1 mg/m³, a maksimum 11,9 mg/m³.
Po uwzględnieniu dnia tygodnia trend ostatnich 30 dni wyniósł {trend:+.4f} mg/m³ na dobę.
Prognoza na 5–11 kwietnia 2005 r. zmienia się zależnie od dnia tygodnia i wynosi od {prog.min():.2f} do {prog.max():.2f} mg/m³.

MAE wyniosło {mae:.2f} mg/m³. To wynik jednego testu na 7 dniach, więc prognoza jest orientacyjna. Różnice między dniami opisują zależności w danych, a nie ich przyczyny.
W systemie IoT przewidywany wzrost CO może pomóc zaplanować częstsze pomiary lub ostrzeżenia. Decyzje powinny uwzględniać również bieżące odczyty czujników.
'''
n['cells'][6]['source']=conclusion.splitlines(keepends=True)
assert len(prog)==7 and prog.notna().all()
assert env['x'].shape[1]==7
assert env['x'].iloc[:,1:].sum(axis=1).le(1).all()
assert env['x'].iloc[:-7].index.max()<env['x'].iloc[-7:].index.min()
p.write_text(json.dumps(n,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
print('OK: notebook wykonany i zapisany, osobne cechy dni tygodnia, chronologiczny podział danych.')
