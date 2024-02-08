from flask import Flask, request, jsonify
import psycopg2
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)


# Configurações do banco de dados
db_config = {
    'host': '',
    'database': 'Cabeleireiro',
    'user': 'postgres',
    'password': '',
    'port': '',
}

# Conexão com o banco de dados
def connect_to_database():
    try:
        connection = psycopg2.connect(**db_config)
        print("Conexão com o banco de dados PostgreSQL estabelecida com sucesso!")
        return connection
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None


#---------------------------------------AGENDAMENTOS tabela 1----------------------------------------------------

'''
TABLE Agendamento (
  Id_Agendamento SERIAL PRIMARY KEY,
  CPF VARCHAR(14) REFERENCES Usuario(CPF),
  Hora_Agendamento TIME,
  Data_Agendamento DATE,
  Valor DECIMAL(10, 2),
  Servico VARCHAR(100)
);
'''

'''
O recurso1 deve disponibilizar as operações de GET e POST na Tabela 1. A operação de GET deve ser capaz de retornar um único elemento (get_by_id). A operação de POST deve ser capaz de inserir um novo registro em uma determinada tabela.
'''

# Rota para obter o CPF do usuário pelo Id_Agendamento
@app.route('/agendamentos/<int:id_agendamento>/usuario', methods=['GET'])
def obter_cpf_pelo_id_agendamento(id_agendamento):
    """
    Obtém o CPF do usuário pelo Id_Agendamento.

    ---
    parameters:
      - name: id_agendamento
        in: path
        type: integer
        required: true
        description: ID do Agendamento

    responses:
      200:
        description: CPF do usuário encontrado
        schema:
          properties:
            CPF:
              type: string
              description: CPF do usuário
      404:
        description: Agendamento não encontrado
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
      500:
        description: Erro interno no servidor
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
    """
    connection = connect_to_database()
    if connection is None:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT Usuario.CPF
                FROM Agendamento
                JOIN Usuario ON Agendamento.CPF = Usuario.CPF
                WHERE Agendamento.Id_Agendamento = %s;
                """,
                (id_agendamento,)
            )
            cpf_usuario = cursor.fetchone()

        if cpf_usuario:
            return jsonify({'CPF': cpf_usuario[0]}), 200
        else:
            return jsonify({'error': 'Agendamento não encontrado'}), 404

    except psycopg2.Error as e:
        print(f"Erro ao obter CPF pelo Id_Agendamento: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

    finally:
        connection.close()

# Rota para cadastrar um novo agendamento
@app.route('/agendamentos', methods=['POST'])
def cadastrar_agendamento():
    """
    Cadastra um novo agendamento.

    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            cpf:
              type: string
              description: CPF do usuário
            hora:
              type: string
              format: time
              description: Hora do agendamento (HH:MM)
            data:
              type: string
              format: date
              description: Data do agendamento (YYYY-MM-DD)
            valor:
              type: number
              format: float
              description: Valor do agendamento
            servico:
              type: string
              description: Tipo de serviço do agendamento

    responses:
      201:
        description: Agendamento criado com sucesso
        schema:
          properties:
            id_agendamento:
              type: integer
              description: ID do novo agendamento
      400:
        description: Campos incompletos no pedido
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
      500:
        description: Erro interno no servidor
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
    """
    data = request.get_json()

    if 'cpf' not in data or 'hora' not in data or 'data' not in data or 'valor' not in data or 'servico' not in data:
        return jsonify({'error': 'Campos incompletos'}), 400

    connection = connect_to_database()
    if connection is None:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO Agendamento (CPF, Hora_Agendamento, Data_Agendamento, Valor, Servico)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING Id_Agendamento;
                """,
                (data['cpf'], data['hora'], data['data'], data['valor'], data['servico'])
            )
            agendamento_id = cursor.fetchone()[0]
            connection.commit()

        return jsonify({'id_agendamento': agendamento_id}), 201

    except psycopg2.Error as e:
        print(f"Erro ao cadastrar agendamento: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

    finally:
        connection.close()

'''
O recurso2 deve disponibilizar a operação de GET em que todos os registros da Tabela 1 devem ser retornados como uma lista de objetos JSON (get_all).
'''
# Rota para consultar todos os agendamentos
@app.route('/agendamentos', methods=['GET'])
def consultar_agendamentos():
    """
    Consulta todos os agendamentos.

    ---
    responses:
      200:
        description: Lista de agendamentos
        schema:
          type: array
          items:
            type: object
            properties:
              Id_Agendamento:
                type: integer
                description: ID do agendamento
              CPF:
                type: string
                description: CPF do usuário
              Hora_Agendamento:
                type: string
                description: Hora do agendamento (HH:MM)
              Data_Agendamento:
                type: string
                description: Data do agendamento (YYYY-MM-DD)
              Valor:
                type: number
                format: float
                description: Valor do agendamento
              Servico:
                type: string
                description: Tipo de serviço do agendamento
      500:
        description: Erro interno no servidor
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
    """
    connection = connect_to_database()
    if connection is None:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Agendamento;")
            agendamentos = cursor.fetchall()

        agendamentos_list = []
        for agendamento in agendamentos:
            agendamento_dict = {
                'Id_Agendamento': agendamento[0],
                'CPF': agendamento[1],
                'Hora_Agendamento': str(agendamento[2]),
                'Data_Agendamento': str(agendamento[3]),
                'Valor': float(agendamento[4]),
                'Servico': agendamento[5]
            }
            agendamentos_list.append(agendamento_dict)

        return jsonify(agendamentos_list).json, 200

    except psycopg2.Error as e:
        print(f"Erro ao consultar agendamentos: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

    finally:
        connection.close()

'''
O recurso3 deve disponibilizar as operações de PUT e DELETE. As operações devem ser capazes de atualizar e apagar da Tabela 1.
'''
# Rota para atualizar um agendamento pelo Id_Agendamento
@app.route('/agendamentos/<int:id_agendamento>', methods=['PUT'])
def atualizar_agendamento(id_agendamento):
    """
    Atualiza um agendamento pelo Id_Agendamento.

    ---
    parameters:
      - name: id_agendamento
        in: path
        type: integer
        required: true
        description: ID do Agendamento a ser atualizado
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            cpf:
              type: string
              description: Novo CPF do usuário
            hora:
              type: string
              format: time
              description: Nova hora do agendamento (HH:MM)
            data:
              type: string
              format: date
              description: Nova data do agendamento (YYYY-MM-DD)
            valor:
              type: number
              format: float
              description: Novo valor do agendamento
            servico:
              type: string
              description: Novo tipo de serviço do agendamento

    responses:
      200:
        description: Agendamento atualizado com sucesso
        schema:
          properties:
            message:
              type: string
              description: Mensagem de sucesso
      400:
        description: Nenhum dado para atualização fornecido
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
      404:
        description: Agendamento não encontrado
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
      500:
        description: Erro interno no servidor
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Nenhum dado para atualização fornecido'}), 400

    connection = connect_to_database()
    if connection is None:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Agendamento WHERE Id_Agendamento = %s;", (id_agendamento,))
            agendamento = cursor.fetchone()

        if not agendamento:
            return jsonify({'error': 'Agendamento não encontrado'}), 404

        with connection.cursor() as cursor:
            update_query = """
                UPDATE Agendamento
                SET CPF = %s, Hora_Agendamento = %s, Data_Agendamento = %s, Valor = %s, Servico = %s
                WHERE Id_Agendamento = %s;
            """
            cursor.execute(
                update_query,
                (
                    data.get('cpf', agendamento[1]),
                    data.get('hora', agendamento[2]),
                    data.get('data', agendamento[3]),
                    data.get('valor', agendamento[4]),
                    data.get('servico', agendamento[5]),
                    id_agendamento
                )
            )
            connection.commit()

        return jsonify({'message': 'Agendamento atualizado com sucesso'}), 200

    except psycopg2.Error as e:
        print(f"Erro ao atualizar agendamento: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

    finally:
        connection.close()


# Rota para excluir um agendamento pelo Id_Agendamento
@app.route('/agendamentos/<int:id_agendamento>', methods=['DELETE'])
def excluir_agendamento(id_agendamento):
    """
    Exclui um agendamento pelo Id_Agendamento.

    ---
    parameters:
      - name: id_agendamento
        in: path
        type: integer
        required: true
        description: ID do Agendamento a ser excluído

    responses:
      200:
        description: Agendamento excluído com sucesso
        schema:
          properties:
            message:
              type: string
              description: Mensagem de sucesso
      404:
        description: Agendamento não encontrado
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
      500:
        description: Erro interno no servidor
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
    """
    connection = connect_to_database()
    if connection is None:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Agendamento WHERE Id_Agendamento = %s;", (id_agendamento,))
            agendamento = cursor.fetchone()

        if not agendamento:
            return jsonify({'error': 'Agendamento não encontrado'}), 404

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Agendamento WHERE Id_Agendamento = %s;", (id_agendamento,))
            connection.commit()

        return jsonify({'message': 'Agendamento excluído com sucesso'}), 200

    except psycopg2.Error as e:
        print(f"Erro ao excluir agendamento: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

    finally:
        connection.close()

# Rota para consultar um agendamento pelo Id_Agendamento => Endpoint EXTRA
@app.route('/agendamentos/<int:id_agendamento>', methods=['GET']) 
def consultar_agendamento(id_agendamento):
    """
    Consulta um agendamento pelo Id_Agendamento.

    ---
    parameters:
      - name: id_agendamento
        in: path
        type: integer
        required: true
        description: ID do Agendamento a ser consultado

    responses:
      200:
        description: Agendamento encontrado
        schema:
          type: object
          properties:
            Id_Agendamento:
              type: integer
              description: ID do agendamento
            CPF:
              type: string
              description: CPF do usuário
            Hora_Agendamento:
              type: string
              description: Hora do agendamento (HH:MM)
            Data_Agendamento:
              type: string
              description: Data do agendamento (YYYY-MM-DD)
            Valor:
              type: number
              format: float
              description: Valor do agendamento
            Servico:
              type: string
              description: Tipo de serviço do agendamento
      404:
        description: Agendamento não encontrado
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
      500:
        description: Erro interno no servidor
        schema:
          properties:
            error:
              type: string
              description: Mensagem de erro
    """
    connection = connect_to_database()
    if connection is None:
        return jsonify({'error': 'Erro ao conectar ao banco de dados'}), 500

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM Agendamento WHERE Id_Agendamento = %s;
                """,
                (id_agendamento,)
            )
            agendamento = cursor.fetchone()

        if agendamento:
            agendamento_dict = {
                'Id_Agendamento': agendamento[0],
                'CPF': agendamento[1],
                'Hora_Agendamento': str(agendamento[2]),
                'Data_Agendamento': str(agendamento[3]),
                'Valor': float(agendamento[4]),
                'Servico': agendamento[5]
            }
            return jsonify(agendamento_dict), 200
        else:
            return jsonify({'error': 'Agendamento não encontrado'}), 404

    except psycopg2.Error as e:
        print(f"Erro ao consultar agendamento: {e}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

    finally:
        connection.close()
    

#---------------------------------------USUÁRIOS Tabela 2---------------------------------------------

'''
TABLE Usuario (
  Nome VARCHAR(100),
  CPF VARCHAR(14) PRIMARY KEY,
  Telefone VARCHAR(15),
  Email VARCHAR(100) UNIQUE,
  Senha VARCHAR(50),
  Data_Nascimento DATE,
  Genero VARCHAR(20)
);
'''

'''
O recurso 4 deve disponibilizar as operações de GET, POST, PUT e DELETE na Tabela 2.
'''
# Método GET para consultar um usuário pelo CPF
@app.route('/usuario/<cpf>', methods=['GET'])
def get_usuario(cpf):
    """
    Consulta um usuário pelo CPF.

    ---
    parameters:
      - name: cpf
        in: path
        type: string
        required: true
        description: CPF do usuário a ser consultado

    responses:
      200:
        description: Usuário encontrado
        schema:
          type: object
          properties:
            Nome:
              type: string
              description: Nome do usuário
            CPF:
              type: string
              description: CPF do usuário
            Telefone:
              type: string
              description: Número de telefone do usuário
            Email:
              type: string
              description: Endereço de e-mail do usuário
            Data_Nascimento:
              type: string
              format: date
              description: Data de nascimento do usuário (YYYY-MM-DD)
            Genero:
              type: string
              description: Gênero do usuário
            Senha:
              type: string
              description: Senha do usuário
      404:
        description: Usuário não encontrado
        schema:
          properties:
            message:
              type: string
              description: Mensagem de erro
      500:
        description: Erro interno no servidor
        schema:
          properties:
            message:
              type: string
              description: Mensagem de erro
    """
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT Nome, CPF, Telefone, Email, Data_Nascimento, Genero, Senha FROM Usuario WHERE CPF = %s;", (cpf,))
        user = cursor.fetchone()
        connection.close()
        if user:
            
            keys = ['Nome', 'CPF', 'Telefone', 'Email', 'Data_Nascimento', 'Genero', 'Senha']
            user_dict = dict(zip(keys, user))
            print(jsonify(user_dict).json)
            return jsonify(user_dict).json, 200
        else:
            return jsonify({'message': 'Usuário não encontrado'}), 404
    else:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500


# Método POST para adicionar um usuário
@app.route('/usuario', methods=['POST'])
def add_usuario():
    """
    Adiciona um novo usuário.

    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            Nome:
              type: string
              description: Nome do usuário
            CPF:
              type: string
              description: CPF do usuário
            Telefone:
              type: string
              description: Número de telefone do usuário
            Email:
              type: string
              description: Endereço de e-mail do usuário
            Senha:
              type: string
              description: Senha do usuário
            Data_Nascimento:
              type: string
              format: date
              description: Data de nascimento do usuário (YYYY-MM-DD)
            Genero:
              type: string
              description: Gênero do usuário

    responses:
      200:
        description: Usuário adicionado com sucesso
        schema:
          type: object
          properties:
            Nome:
              type: string
              description: Nome do usuário
            CPF:
              type: string
              description: CPF do usuário
            Telefone:
              type: string
              description: Número de telefone do usuário
            Email:
              type: string
              description: Endereço de e-mail do usuário
            Senha:
              type: string
              description: Senha do usuário
            Data_Nascimento:
              type: string
              format: date
              description: Data de nascimento do usuário (YYYY-MM-DD)
            Genero:
              type: string
              description: Gênero do usuário
      500:
        description: Erro interno no servidor
        schema:
          properties:
            message:
              type: string
              description: Mensagem de erro
    """
    new_user = request.get_json()
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Usuario (Nome, CPF, Telefone, Email, Senha, Data_Nascimento, Genero) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *;",
                       (new_user['Nome'], new_user['CPF'], new_user['Telefone'], new_user['Email'], new_user['Senha'], new_user['Data_Nascimento'], new_user['Genero']))
        connection.commit()
        added_user = cursor.fetchone()
        connection.close()
        return jsonify(added_user), 200
    else:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500

# Método PUT para atualizar os dados de um usuário pelo CPF
@app.route('/usuario/<cpf>', methods=['PUT'])
def update_usuario(cpf):
    """
    Atualiza os dados de um usuário pelo CPF.

    ---
    parameters:
      - name: cpf
        in: path
        type: string
        required: true
        description: CPF do usuário a ser atualizado
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            Nome:
              type: string
              description: Novo nome do usuário
            Telefone:
              type: string
              description: Novo número de telefone do usuário
            Email:
              type: string
              description: Novo endereço de e-mail do usuário
            Senha:
              type: string
              description: Nova senha do usuário
            Data_Nascimento:
              type: string
              format: date
              description: Nova data de nascimento do usuário (YYYY-MM-DD)
            Genero:
              type: string
              description: Novo gênero do usuário

    responses:
      200:
        description: Usuário atualizado com sucesso
        schema:
          type: object
          properties:
            Nome:
              type: string
              description: Nome atualizado do usuário
            CPF:
              type: string
              description: CPF atualizado do usuário
            Telefone:
              type: string
              description: Número de telefone atualizado do usuário
            Email:
              type: string
              description: Endereço de e-mail atualizado do usuário
            Senha:
              type: string
              description: Senha atualizada do usuário
            Data_Nascimento:
              type: string
              format: date
              description: Data de nascimento atualizada do usuário (YYYY-MM-DD)
            Genero:
              type: string
              description: Gênero atualizado do usuário
      404:
        description: Usuário não encontrado
        schema:
          properties:
            message:
              type: string
              description: Mensagem de erro
      500:
        description: Erro interno no servidor
        schema:
          properties:
            message:
              type: string
              description: Mensagem de erro
    """
    updated_data = request.get_json()
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE Usuario SET Nome = %s, Telefone = %s, Email = %s, Senha = %s, Data_Nascimento = %s, Genero = %s WHERE CPF = %s RETURNING *;",
                       (updated_data['Nome'], updated_data['Telefone'], updated_data['Email'], updated_data['Senha'], updated_data['Data_Nascimento'], updated_data['Genero'], cpf))
        connection.commit()
        updated_user = cursor.fetchone()
        connection.close()
        if updated_user:
            return jsonify(updated_user), 200
        else:
            return jsonify({'message': 'Usuário não encontrado'}), 404
    else:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500

# Método DELETE para excluir um usuário pelo CPF
@app.route('/usuario/<cpf>', methods=['DELETE'])
def delete_usuario(cpf):
    """
    Exclui um usuário pelo CPF.

    ---
    parameters:
      - name: cpf
        in: path
        type: string
        required: true
        description: CPF do usuário a ser excluído

    responses:
      200:
        description: Usuário excluído com sucesso
        schema:
          type: object
          properties:
            Nome:
              type: string
              description: Nome do usuário excluído
            CPF:
              type: string
              description: CPF do usuário excluído
            Telefone:
              type: string
              description: Número de telefone do usuário excluído
            Email:
              type: string
              description: Endereço de e-mail do usuário excluído
            Senha:
              type: string
              description: Senha do usuário excluído
            Data_Nascimento:
              type: string
              format: date
              description: Data de nascimento do usuário excluído (YYYY-MM-DD)
            Genero:
              type: string
              description: Gênero do usuário excluído
      404:
        description: Usuário não encontrado
        schema:
          properties:
            message:
              type: string
              description: Mensagem de erro
      500:
        description: Erro interno no servidor
        schema:
          properties:
            message:
              type: string
              description: Mensagem de erro
    """
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Usuario WHERE CPF = %s RETURNING *;", (cpf,))
        connection.commit()
        deleted_user = cursor.fetchone()
        connection.close()
        if deleted_user:
            return jsonify(deleted_user), 200
        else:
            return jsonify({'message': 'Usuário não encontrado'}), 404
    else:
        return jsonify({'message': 'Erro de conexão com o banco de dados'}), 500
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)