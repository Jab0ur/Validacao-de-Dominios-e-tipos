import socket
import requests
import pandas as pd

# Caminho para seu arquivo de entrada (.txt com um subdomínio por linha)
entrada = "subdominios.txt"

# Lista para armazenar os resultados
resultados = []

# Ler cada linha do arquivo
with open(entrada, "r") as arquivo:
    dominios = [linha.strip() for linha in arquivo if linha.strip()]

for dominio in dominios:
    resultado = {
        "Subdomínio": dominio,
        "Resolve DNS": False,
        "IP Resolvido": "",
        "HTTP Online": False,
        "HTTP Status": "",
        "Observações": ""
    }

    # Verificar DNS
    try:
        ip = socket.gethostbyname(dominio)
        resultado["Resolve DNS"] = True
        resultado["IP Resolvido"] = ip
    except socket.gaierror:
        resultado["Observações"] = "Não resolve DNS"

    # Verificar HTTP/HTTPS apenas se resolve DNS
    if resultado["Resolve DNS"]:
        for protocolo in ["http://", "https://"]:
            try:
                response = requests.head(protocolo + dominio, timeout=10, allow_redirects=True, verify=False)
                resultado["HTTP Online"] = True
                resultado["HTTP Status"] = response.status_code
                break
            except requests.RequestException:
                continue
        if not resultado["HTTP Online"]:
            resultado["Observações"] = "DNS OK, mas HTTP falhou"

    resultados.append(resultado)

# Exportar para Excel
df = pd.DataFrame(resultados)
df.to_excel("resultado_validacao_dns_http.xlsx", index=False)

print("✅ Validação finalizada! Arquivo gerado: resultado_validacao_dns_http.xlsx")
