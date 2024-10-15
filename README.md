
# Preço Bitcoin API

Esta é uma API desenvolvida em Python com FastAPI para consultar o preço de uma moeda específica, como o Bitcoin (BTC), a partir da API do Mercado Bitcoin e se não estiver disponível, irá usar a da CoinGecko. A API também utiliza Redis para cachear as consultas e otimizar o desempenho.

## Requisitos

- Python 3.9 ou superior
- Redis
- Google Chrome ou Chromium instalado
- Dependências listadas no arquivo `requirements.txt`

## Configuração e Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/Lexnoronha/preco_bitcoin.git
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure o Redis localmente. Certifique-se de que o Redis está rodando na porta 6379.

4. Adicione um arquivo `users.json` no diretório raiz do projeto, contendo os usuários autorizados para autenticação básica:
   ```json
   {
     "users": [
       {
         "username": "usuario",
         "password": "senha"
       }
     ]
   }
   ```

5. Insira o comando `make` para facilitar a execução da API:
   ```bash
   make api
   ```

## Como Usar

### Endpoint para consulta de preços

- **URL:** `/coin_infos/`
- **Método:** `POST`
- **Payload de Requisição:**
  ```json
  {
    "symbol": "BTC"
  }
  ```

### Exemplo de Resposta:
```json
{
  "coin_name": "Bitcoin",
  "symbol": "BTC",
  "coin_price": 200.501231,
  "coin_price_dolar": "40.039391",
  "date_consult": "2024-10-14 21:35:06"
}
```

### Autenticação

Esta API utiliza autenticação básica. Para acessar o endpoint, você precisa fornecer o nome de usuário e senha que estão definidos no arquivo `users.json`.

## Funcionalidades

1. **Consulta de preço:** A API consulta o preço da moeda no Mercado Bitcoin ou na CoinGecko caso o primeiro serviço não esteja disponível.
2. **Cache Redis:** Para otimizar a performance, as consultas são armazenadas em cache no Redis por 60 segundos.
3. **Taxa de câmbio:** A resposta inclui também o valor da moeda em relação ao dólar americano, usando a taxa de câmbio atual obtida de uma API externa.
4. **Autenticação Básica:** Apenas usuários autenticados podem consultar os preços.
5. **Sistema de cache:** Implementado com Redis, as consultas de preços são armazenadas por 60 segundos para reduzir o número de chamadas às APIs externas.
6. **Autenticação básica:** Apenas usuários autorizados, definidos no arquivo `users.json`, podem acessar os endpoints da API.