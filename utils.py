def dividir_texto(texto, max_length=2000):
    return [texto[i:i + max_length] for i in range(0, len(texto), max_length)]