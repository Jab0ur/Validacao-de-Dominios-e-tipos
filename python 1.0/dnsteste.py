import socket
import requests
import pandas as pd
import dns.resolver
import urllib3
import os
from tqdm import tqdm

# Desativar warning de certificado SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Garantir que C:\Temp exista
os.makedirs(r"C:\Temp", exist_ok=True)

entrada = "subdominios.txt"
resultados = []
tipos_dns = ["A", "CNAME", "MX", "TXT"]

# Ler domínios do arquivo
with open(entrada, "r") as arquivo:
    dominios = [linha.strip() for linha in arquivo if linha.strip()]

# Loop com barra de progresso
for dominio in tqdm(dominios, desc="Validando DNS e HTTP", unit="domínio"):
    resultado = {
        "Subdomínio": dominio,
        "Tipo DNS Encontrado": "",
        "Valores DNS": "",
        "IP Resolvido": "",
        "HTTP Online": False,
        "HTTP Status": "",
        "Observações": ""
    }

    tipos_encontrados = []
    valores_dns = []

    for tipo in tipos_dns:
        try:
            resposta = dns.resolver.resolve(dominio, tipo, lifetime=3)
            tipos_encontrados.append(tipo)

            for r in resposta:
                valores_dns.append(f"{tipo}: {r.to_text()}")

            if tipo == "A":
                resultado["IP Resolvido"] = resposta[0].to_text()

        except:
            continue

    if tipos_encontrados:
        resultado["Tipo DNS Encontrado"] = ", ".join(tipos_encontrados)
        resultado["Valores DNS"] = "; ".join(valores_dns)
    else:
        resultado["Observações"] = "Não resolve DNS"

    # Verificar HTTP/HTTPS apenas se tem IP resolvido (registro A)
    if resultado["IP Resolvido"]:
        for protocolo in ["http://", "https://"]:
            try:
                response = requests.head(protocolo + dominio, timeout=10, allow_redirects=True, verify=False)
                resultado["HTTP Online"] = True
                resultado["HTTP Status"] = response.status_code
                break
            except:
                continue
        if not resultado["HTTP Online"]:
            resultado["Observações"] = "DNS OK, mas HTTP falhou"

    resultados.append(resultado)

# Exportar para Excel
df = pd.DataFrame(resultados)
df.to_excel(r"C:\Temp\resultado_validacao_dns_http.xlsx", index=False)

print("\n✅ Validação finalizada! Arquivo salvo em: C:\\Temp\\resultado_validacao_dns_http.xlsx")
print("✅ Domínios com erro de DNS ou HTTP foram registrados.")
print("✅ Verifique o arquivo para mais detalhes.") 