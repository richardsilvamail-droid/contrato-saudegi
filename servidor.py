f#!/usr/bin/env python3
"""
Editor de Contrato - Saúde GI
Rode: python servidor.py
Depois acesse: http://localhost:8080
"""
import http.server, json, subprocess, tempfile, shutil, os, base64, re, webbrowser, sys

BASE = os.path.dirname(os.path.abspath(__file__))
DOCX_SRC = os.path.join(BASE, 'contrato_modelo.docx')
HTML_FILE = os.path.join(BASE, 'app_contrato.html')

PRICE_LINES = [
    ('EXAME CLÍNICO',          ' R$ 40,00 '),
    ('ACUIDADE VISUAL',        ' R$ 20,00 '),
    ('AUDIOMETRIA',            ' R$ 30,00 '),
    ('ESPIROMETRIA',           ' R$ 30,00 '),
    ('HEMOGRAMA',              ' R$ 17,00 '),
    ('GLICEMIA',               ' R$ 11,00 '),
    ('RETICULÓCITOS',          ' R$ 8,00 '),
    ('GAMA GT',                ' R$ 8,00 '),
    ('TGO',                    ' R$ 8,00 '),
    ('TGP',                    ' R$ 8,00 '),
    ('ACIDO TRANSMUCONICO',    ' R$ 56,00 '),
    ('CARBOXI-HEMOGLOBINA',    ' R$ 44,00 '),
    ('RX TÓRAX - OIT',         ' R$ 44,00 '),
    ('AVALIAÇÃO PSICOSSOCIAL (C/MÉDICO)', ' R$ 65,00 '),
    ('PGR-PROGRAMA DE GERENCIAMENTO DE RISCOS (AVAL. AMBIENTAIS NÃO INCLUSAS)', ' R$ 300,00 '),
    ('PCMSO-PROGRAMA DE CONTROLE MÉDICO DE SAÚDE OCUPACIONAL', ' R$ 300,00 '),
    ('LTCAT-LAUDO TÉCNICO DAS CONDIÇÕES AMBIENTAIS DE TRABALHO (AVAL. AMBIENTAIS NÃO INCLUSAS)', ' R$ 300,00 '),
    ('MONÓXIDO DE CARBONO ',   ' R$ 685,00 '),
    ('RUÍDO (AUDIODOSIMETRIA)',' R$ 255,00 '),
    ('VIBRAÇÃO CORPO INTEIRO', ' R$ 775,00 '),
]

def gerar_docx(dados):
    import zipfile
    tmpdir = tempfile.mkdtemp()
    try:
        # Extrair o docx (é um zip)
        unpacked = os.path.join(tmpdir, 'unpacked')
        os.makedirs(unpacked)
        with zipfile.ZipFile(DOCX_SRC, 'r') as z:
            z.extractall(unpacked)

        doc = os.path.join(unpacked, 'word', 'document.xml')
        with open(doc, 'r', encoding='utf-8') as f:
            xml = f.read()

        # Substituições principais
        xml = xml.replace('CONDOMINIO RESIDENCIAL LIMEIRA TENIS CLUBE', dados['nome'])
        xml = xml.replace('05.066.792/0001-10', dados['cnpj'])
        xml = xml.replace('carolinasindicalimeira@hotmail.com', dados['email'])
        xml = xml.replace(
            'Av. Prof. Darcy Ribeiro, nº 100 - Bairro Morada da Colina, CEP: 27.512230',
            dados['endereco']
        )

        # Substituição de preços linha a linha
        precos = dados.get('precos', {})
        lines = xml.split('\n')
        last_desc = None
        for i, line in enumerate(lines):
            m = re.search(r'<w:t[^>]*>([^<]+)</w:t>', line)
            if m:
                txt = m.group(1).strip()
                for desc, old_val in PRICE_LINES:
                    if txt == desc.strip():
                        last_desc = desc
                        break
                else:
                    if last_desc and last_desc in precos:
                        for desc2, old_val2 in PRICE_LINES:
                            if desc2 == last_desc and old_val2 in line:
                                novo = ' ' + precos[last_desc] + ' '
                                lines[i] = line.replace(old_val2, novo)
                                last_desc = None
                                break
        xml = '\n'.join(lines)

        with open(doc, 'w', encoding='utf-8') as f:
            f.write(xml)

        # Reempacotar como docx
        out = os.path.join(tmpdir, 'contrato_novo.docx')
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
            for root, dirs, files in os.walk(unpacked):
                for file in files:
                    fp = os.path.join(root, file)
                    arcname = os.path.relpath(fp, unpacked)
                    zout.write(fp, arcname)

        with open(out, 'rb') as f:
            return f.read()
    finally:
        shutil.rmtree(tmpdir)

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f'  [{self.address_string()}] {format % args}')

    def do_GET(self):
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html = f.read().encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        dados = json.loads(body)
        try:
            docx = gerar_docx(dados)
            b64 = base64.b64encode(docx).decode()
            resp = json.dumps({'ok': True, 'file': b64}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(resp))
            self.end_headers()
            self.wfile.write(resp)
            print(f'  ✅ Contrato gerado para: {dados["nome"]}')
        except Exception as e:
            resp = json.dumps({'ok': False, 'error': str(e)}).encode()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(resp)
            print(f'  ❌ Erro: {e}')

if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 8080))

    print('='*50)
    print('Editor de Contrato — Saúde GI')
    print('='*50)
    print(f'Servidor iniciado na porta {PORT}')
    print('='*50)

    try:
        http.server.HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print('\nServidor encerrado.')