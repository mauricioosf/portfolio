# Confere se o PDF do currículo gerado a partir do site está completo antes de publicá-lo.
# Uso: python checar_curriculo.py <videos.json> <pdf gerado> <destino>
# Só copia o PDF para o destino se ele tiver o nome e todas as experiências, formações e
# formações complementares do videos.json. Caso contrário sai com erro e o destino fica como estava.
import json, os, re, shutil, sys
from pypdf import PdfReader

dados, pdf, destino = sys.argv[1:4]
about = json.load(open(dados, encoding='utf-8')).get('about', {})

def pt(v):
    return (v.get('pt') if isinstance(v, dict) else v) or ''

def norm(s):
    # Ignora espaços e hifens de quebra de linha (o texto do PDF é hifenizado).
    return re.sub(r'[\s\-­]+', '', s).lower()

esperado = [about.get('name') or 'Mauricio Ferreira']
for secao in ('timeline', 'education', 'licenses'):
    for item in about.get(secao, []):
        # " // " no cargo vira quebra de linha no site; cada parte é conferida separada.
        esperado += [p.strip() for p in re.split(r'(?:^|\s)//(?:\s|$)', pt(item.get('role'))) if p.strip()]

# Textos próprios do currículo: confere o começo de cada um, para garantir que o
# curriculo.json carregou antes da impressão.
arq_cv = os.path.join(os.path.dirname(os.path.abspath(dados)), 'curriculo.json')
if os.path.exists(arq_cv):
    cv = json.load(open(arq_cv, encoding='utf-8'))
    cargos = {pt(item.get('role')).strip() for item in about.get('timeline', [])}
    textos = [pt(cv.get('bio')).split('\n\n')[-1]]
    textos += [pt(t) for cargo, t in (cv.get('experiencias') or {}).items() if cargo in cargos]
    esperado += [t[:40] for t in textos if t.strip()]

leitor = PdfReader(pdf)
paginas = len(leitor.pages)
texto = norm(' '.join(p.extract_text() or '' for p in leitor.pages))
faltando = [s for s in esperado if norm(s) not in texto]

if not 1 <= paginas <= 6:
    sys.exit('PDF com %d páginas, fora do esperado; mantendo o currículo anterior.' % paginas)
if faltando:
    sys.exit('Itens que não apareceram no PDF: %s; mantendo o currículo anterior.' % '; '.join(faltando))

shutil.copyfile(pdf, destino)
print('Currículo atualizado: %d páginas, %d itens conferidos.' % (paginas, len(esperado)))
