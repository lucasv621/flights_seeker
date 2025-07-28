import requests
import telegram
import asyncio
import time
import os

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
PRECIO_MAXIMO_DESEADO = 2000

async def buscar_y_enviar():
    """
    Esta función busca los vuelos y envía el mensaje.
    Está diseñada para ser ejecutada una sola vez por el programador.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: No se encontraron las variables de entorno TELEGRAM_TOKEN o TELEGRAM_CHAT_ID.")
        return

    print("Iniciando búsqueda de vuelos en Level...")
    
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    destinations = ['BCN', 'MAD']
    vuelos_encontrados_global = []

    try:
        url_calendario = "https://www.flylevel.com/nwe/flights/api/calendar/"
        
        for month in months:
            for destination in destinations:
                print(f"Buscando vuelos a {destination} para el mes {month}/2026...")
                params = {
                    'triptype': 'OW', 'origin': 'EZE', 'destination': destination,
                    'month': str(month), 'year': '2026', 'currencyCode': 'USD'
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url_calendario, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if 'data' in data and 'dayPrices' in data['data']:
                    for dia in data['data']['dayPrices']:
                        if 'price' in dia and dia['price'] is not None and dia['price'] <= PRECIO_MAXIMO_DESEADO:
                            vuelo = {"destination": destination, "date": dia['date'], "price": dia['price']}
                            vuelos_encontrados_global.append(vuelo)
                time.sleep(1)

        if vuelos_encontrados_global:
            vuelos_encontrados_global.sort(key=lambda v: v['price'])
            total_ofertas = len(vuelos_encontrados_global)
            print(f'Búsqueda finalizada. Se encontraron {total_ofertas} ofertas.')
            top_vuelos = vuelos_encontrados_global[:10]
            
            mensaje_final = f"🎉 ¡Se encontraron {total_ofertas} ofertas!\n\nMostrando las 10 más baratas:\n\n"
            for vuelo in top_vuelos:
                mensaje_final += f"✈️ Vuelo a {vuelo['destination']}: {vuelo['date']} por ${vuelo['price']} USD.\n"
            
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensaje_final)
        else:
            print("Búsqueda finalizada. No se encontraron ofertas que cumplan el criterio.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")
        # Print

if __name__ == '__main__':
    asyncio.run(buscar_y_enviar())