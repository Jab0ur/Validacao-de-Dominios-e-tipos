import pandas as pd
import dns.resolver
import urllib3
import os
from tqdm import tqdm

# Desativar warnings de certificado SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Garantir que o diretório C:\Temp exista
os.makedirs(r"C:\Temp", exist_ok=True)

entrada = "dns_domain_type_pairs.txt"
resultados = []

# Ler os pares de domínio,tipo
with open(entrada, "r") as arquivo:
    linhas = [linha.strip() for linha in arquivo if linha.strip()]

# Loop para cada linha do arquivo
for linha in tqdm(linhas, desc="Validando Registros DNS", unit="registro"):
    try:
        dominio, tipo = linha.split(",", 1)
    except ValueError:
        continue  # Ignorar linhas mal formatadas

    resultado = {
        "Domínio": dominio,
        "Tipo Consultado": tipo,
        "Valor Retornado": "",
        "IP Resolvido": "",
        "CNAME Destino": "",
        "Observações": ""
    }

    try:
        resposta = dns.resolver.resolve(dominio, tipo, lifetime=3)
        valores = [r.to_text() for r in resposta]
        resultado["Valor Retornado"] = "; ".join(valores)

        if tipo == "A":
            resultado["IP Resolvido"] = resposta[0].to_text()

        if tipo == "CNAME":
            resultado["CNAME Destino"] = resposta[0].to_text()

    except dns.resolver.NXDOMAIN:
        resultado["Observações"] = "NXDOMAIN - Domínio não existe"
    except dns.resolver.NoAnswer:
        resultado["Observações"] = "NoAnswer - Tipo não encontrado"
    except dns.resolver.NoNameservers:
        resultado["Observações"] = "NoNameservers - Sem servidores"
    except dns.resolver.Timeout:
        resultado["Observações"] = "Timeout - Consulta demorou demais"
    except Exception as e:
        resultado["Observações"] = f"Erro: {e}"

    resultados.append(resultado)

# Exportar para Excel
df = pd.DataFrame(resultados)
df.to_excel(r"C:\Temp\resultado_dns_verificacao.xlsx", index=False)

print("\n✅ Verificação concluída! Resultado salvo em: C:\\Temp\\resultado_dns_verificacao.xlsx")
