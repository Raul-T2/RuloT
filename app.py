from flask import Flask, render_template, request 
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Definimos los tokens
tokens = [
    'INT', 'MAIN', 'PARENTESIS_IZQUIERDA', 'PARENTESIS_DERECHA', 'LLAVE_IZQUIERDA', 'LLAVE_DERECHA', 'PUNTO_Y_COMA', 'ID', 'IDENTIFICADOR'
]

# Reglas de los tokens con nombres descriptivos
t_PARENTESIS_IZQUIERDA = r'\('
t_PARENTESIS_DERECHA = r'\)'
t_LLAVE_IZQUIERDA = r'\{'
t_LLAVE_DERECHA = r'\}'
t_PUNTO_Y_COMA = r';'

# Diccionario de palabras reservadas
reserved = {
    'int': 'INT',
    'main': 'MAIN'
}

# Añadimos la regla para reconocer "x" como IDENTIFICADOR
def t_IDENTIFICADOR(t):
    r'x'
    return t

# Función para reconocer identificadores generales
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')  # Verifica si es una palabra reservada
    return t

t_ignore = ' \t\n'

def t_error(t):
    t.lexer.skip(1)

# Construimos el analizador léxico
lexer = lex.lex()

# Definimos la gramática para el parser
def p_program(p):
    '''program : INT MAIN PARENTESIS_IZQUIERDA PARENTESIS_DERECHA LLAVE_IZQUIERDA declarations LLAVE_DERECHA'''
    p[0] = "Estructura Correcta"

def p_declarations(p):
    '''declarations : INT IDENTIFICADOR PUNTO_Y_COMA
                    | INT IDENTIFICADOR PUNTO_Y_COMA declarations'''
    p[0] = "Declaración Correcta"

def p_error(p):
    if p:
        if p.type == 'ID':
            p[0] = f"Error: Se esperaba 'x', pero se encontró '{p.value}' en la línea {p.lineno}"
        else:
            p[0] = f"Error de sintaxis en '{p.value}' en la línea {p.lineno}"
    else:
        p[0] = "Error de sintaxis al final de la entrada"

parser = yacc.yacc()

@app.route("/", methods=["GET", "POST"])
def index():
    text = ""
    estructura_valida = None
    errores = []
    tabla_lexico = []
    tabla_sintactica = []

    if request.method == "POST":
        text = request.form["text"]
        lexer.input(text)
        
        # Obtener los tokens y formar la tabla léxica
        line_number = 1
        current_line_tokens = []
        
        while True:
            tok = lexer.token()
            if not tok:
                if current_line_tokens:
                    tabla_lexico.append((line_number, current_line_tokens))
                break
            # Modificamos la forma en que se agrega el tipo de token
            if tok.type in ['INT', 'MAIN']:
                token_type = "Palabra Reservada"
            else:
                token_type = tok.type.replace('_', ' ').lower()
                
            current_line_tokens.append((token_type, tok.value))
            if tok.type == 'PUNTO_Y_COMA' or tok.type == 'LLAVE_DERECHA':
                tabla_lexico.append((line_number, current_line_tokens))
                current_line_tokens = []
                line_number += 1
        
        # Verificación sintáctica
        resultado = parser.parse(text)
        if resultado == "Estructura Correcta":
            tabla_sintactica = [(line_number, "Estructura válida", "✔")]
        else:
            errores.append(resultado)
            tabla_sintactica = [(line_number, "Estructura inválida", "✘")]

    return render_template("index.html", tabla_lexico=tabla_lexico, text=text, estructura_valida=estructura_valida, errores=errores, tabla_sintactica=tabla_sintactica)

if __name__ == "__main__":
    app.run(debug=True)
