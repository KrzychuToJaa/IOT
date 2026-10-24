from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
from lxml import etree as E
import hashlib,shutil
base=Path.cwd();qa=base/'.tmp_report';ref=base/'Zadanie 1/Raport_zadanie_1.docx';target=base/'Zadanie 2/Raport_zadanie_2.docx'
shutil.copy2(target,qa/'Raport_zadanie_2_przed_zmianami.docx')
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
w=lambda s:'{'+ns['w']+'}'+s
with ZipFile(ref) as z:r=E.fromstring(z.read('word/document.xml'))
with ZipFile(target) as z:parts={n:z.read(n) for n in z.namelist()};infos=z.infolist()
d=E.fromstring(parts['word/document.xml']);body=d.find('w:body',ns);rp=r.findall('w:body/w:p',ns);op=body.findall('w:p',ns)
(qa/'artifact.md').write_text(f'''Reference: {ref}\nSHA256: {hashlib.sha256(ref.read_bytes()).hexdigest()}\nReference render: original_1.pdf and original_1_page_1.png to page_2.png\nTwo pages, one A4 section, margins top/bottom 1.799 cm, left/right 2.000 cm.\nKeep report 2 package unchanged except word/document.xml. Styles, numbering, relationships, images, theme, metadata and section geometry preserved.\nUse reference paragraph 0 for left aligned bold 21 pt Title; 1 to 3 metadata; 4 for bold 13 pt headings; 5 for 11 pt Calibri prose with 6 pt after and 1.05 spacing; 12 for Consolas 9 pt code with existing gray shading; 34 for bold captions; 35 for centered images.\nSections in order: Architektura systemu, Użyte narzędzia, Fragment kodu, Wizualizacja danych. Shorten report 2 prose and diagram, fix lamp presence condition to match sterownik.py. Retain author, date and all three images from report 2. Page two contains visualization and screenshots. Dashboard may be scaled proportionally to fit captions. No tables, headers, footers or fields in content slots.\n''',encoding='utf-8')
def para(template,text):
 p=deepcopy(template)
 for x in list(p):
  if x.tag!=w('pPr'):p.remove(x)
 run=E.SubElement(p,w('r'))
 old=template.find('w:r/w:rPr',ns)
 if old is not None:run.append(deepcopy(old))
 t=E.SubElement(run,w('t'));t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=text
 return p
new=[]
def add(idx,text):new.append(para(rp[idx],text));return new[-1]
for idx in range(4):add(idx,op[idx].xpath('string(.)'))
add(4,'Architektura systemu')
add(5,'Celem zadania jest symulacja inteligentnego domu, w którym lampa i klimatyzacja reagują na światło, temperaturę oraz obecność użytkownika. Program dom.py symuluje czujniki i urządzenia, a sterownik.py odbiera pomiary i wysyła polecenia.')
add(6,'dom.py → broker MQTT → sterownik.py  (pomiary)')
add(7,'sterownik.py → broker MQTT → dom.py  (polecenia)')
add(8,'sterownik.py → HTTP POST przez HTTPS → ThingSpeak')
add(9,'Użyte narzędzia')
add(10,'Python losuje temperaturę od 20 do 32°C i poziom światła od 0 do 100 co 20 sekund. Użytkownik podaje obecność przy uruchomieniu: 1 oznacza, że jest w domu, a 0, że go nie ma. Biblioteka paho-mqtt przesyła wiadomości przez broker test.mosquitto.org, a requests wysyła dane do ThingSpeak.')
add(10,'Lampa włącza się przy świetle poniżej 30 i obecności użytkownika. Klimatyzacja włącza się przy temperaturze powyżej 28°C i obecności użytkownika. W pozostałych przypadkach urządzenia są wyłączone, a ich stan jest wypisywany w terminalu.')
add(11,'Fragment kodu')
code=['if swiatlo < 30 and obecnosc == 1:','    lampa = 1','else:','    lampa = 0','if temperatura > 28 and obecnosc == 1:','    klimatyzacja = 1','else:','    klimatyzacja = 0']
for line in code:add(12,line)
p=add(32,'Wizualizacja danych');pp=p.find('w:pPr',ns);E.SubElement(pp,w('pageBreakBefore'))
add(33,'Dashboard ThingSpeak pokazuje temperaturę, poziom światła, obecność użytkownika oraz stan lampy i klimatyzacji w polach Field 1–5. Dla obecności i urządzeń wartość 1 oznacza stan aktywny, a 0 nieaktywny.')
for caption,source in [('Rysunek 1. Działająca symulacja przy obecności użytkownika',op[32]),('Rysunek 2. Działająca symulacja przy nieobecności użytkownika',op[33]),('Rysunek 3. Dashboard ThingSpeak',op[35])]:
 cap=add(34,caption)
 pp=cap.find('w:pPr',ns);E.SubElement(pp,w('keepNext'))
 image=deepcopy(source)
 for el in image.xpath('.//w:t | .//w:br',namespaces=ns):el.getparent().remove(el)
 pp=image.find('w:pPr',ns)
 if pp is not None:image.remove(pp)
 image.insert(0,deepcopy(rp[35].find('w:pPr',ns)))
 if source is op[35]:
  ratio=12.0/13.798911111111112
  for el in image.xpath('.//wp:extent | .//a:ext',namespaces=ns):
   for attr in ['cx','cy']:
    if attr in el.attrib:el.set(attr,str(round(int(el.get(attr))*ratio)))
 new.append(image)
for child in list(body):
 if child.tag!=w('sectPr'):body.remove(child)
for i,p in enumerate(new):body.insert(i,p)
parts['word/document.xml']=E.tostring(d,xml_declaration=True,encoding='UTF-8',standalone=True)
target = base/'Zadanie 2/Raport_zadanie_2_uproszczony.docx'
with ZipFile(target,'w') as z:
 for info in infos:z.writestr(info,parts[info.filename])
with ZipFile(qa/'Raport_zadanie_2_przed_zmianami.docx') as old,ZipFile(target) as final:
 changed=[n for n in old.namelist() if old.read(n)!=final.read(n)]
 print('Changed package parts:',changed)
 assert changed==['word/document.xml']
print('Saved',target)

