create database centro_logistica;
use centro_logistica;

create table localidade (
    id_loc int auto_increment primary key,
    cidade_loc varchar(255) not null,
    estado_loc varchar(255) not null,
    pais_loc varchar(255) not null,
    bairro_loc varchar(255) not null,
    numero_loc int not null,
    cep_loc varchar(20) not null,
    ponto_refer_loc varchar(255) not null,
    complemento_loc varchar(255) not null
);

create table cliente (
    id_cli int auto_increment primary key,
    nome_cli varchar(255) not null,
    cpf_cli varchar(20) not null,
    email_cli varchar(255) not null,
    telefone_cli varchar(20) not null,
    data_nasc_cli date not null,
    id_loc_fk int,
    foreign key (id_loc_fk) references localidade(id_loc)
);

create table distribuidora(
    id_dist int auto_increment primary key,
    nome_dist varchar(255) not null,
    capacidade_dist double not null,
    cnpj_dist varchar(20) not null,
    email_dist varchar(255) not null,
    telefone_dist varchar(20) not null,
    id_loc_fk int,
    foreign key (id_loc_fk) references localidade(id_loc)
);

create table pedido (
    id_ped int auto_increment primary key,
    data_entrada_ped date not null,
    prazo_entrega_ped date not null,
    altura_ped double not null,
    largura_ped double not null,
    comprimento_ped double not null,
    tara_ped double not null,
    peso_ped double not null,
    adendos_ped varchar(255) not null,
    status_ped varchar(50) not null,
    id_origem_loc_fk int,
    id_destino_loc_fk int,
    id_cli_fk int,
    id_dist_fk int,
    foreign key (id_origem_loc_fk) references localidade(id_loc),
    foreign key (id_destino_loc_fk) references localidade(id_loc),
    foreign key (id_cli_fk) references cliente(id_cli),
    foreign key (id_dist_fk) references distribuidora(id_dist)
);

INSERT INTO localidade 
(cidade_loc, estado_loc, pais_loc, bairro_loc, numero_loc, cep_loc, ponto_refer_loc, complemento_loc, regiao_loc)
VALUES
('Porto Velho', 'Rondônia', 'Brasil', 'Centro', 100, '76801-000', 'Próximo ao mercado central', 'Sala 1', 'Norte'),
('Salvador', 'Bahia', 'Brasil', 'Barra', 200, '40140-110', 'Perto do Farol da Barra', 'Apto 202', 'Nordeste'),
('Cuiabá', 'Mato Grosso', 'Brasil', 'Duque de Caxias', 300, '78043-000', 'Ao lado do shopping', 'Bloco B', 'Centro-Oeste'),
('São Paulo', 'São Paulo', 'Brasil', 'Vila Mariana', 400, '04101-000', 'Próximo ao metrô', 'Casa', 'Sudeste'),
('Curitiba', 'Paraná', 'Brasil', 'Batel', 500, '80420-090', 'Em frente ao shopping', 'Cobertura', 'Sul'),
('Cuiabá', 'Mato Grosso', 'Brasil', 'Centro Norte', 150, '78005-000', 'Próximo ao parque', 'Casa', 'Centro-Oeste');

INSERT INTO cliente 
(nome_cli, cpf_cli, email_cli, telefone_cli, data_nasc_cli, id_loc_fk)
VALUES
('João Silva', '123.456.789-00', 'joao.silva@email.com', '69999990001', '1990-05-10', 1),
('Maria Oliveira', '234.567.890-11', 'maria.oliveira@email.com', '69999990002', '1985-08-22', 2),
('Carlos Souza', '345.678.901-22', 'carlos.souza@email.com', '69999990003', '1992-11-15', 3),
('Ana Santos', '456.789.012-33', 'ana.santos@email.com', '69999990004', '1998-03-05', 4),
('Pedro Costa', '567.890.123-44', 'pedro.costa@email.com', '69999990005', '1980-12-30', 5);

INSERT INTO distribuidora
(nome_dist, capacidade_dist, cnpj_dist, email_dist, telefone_dist, id_loc_fk)
VALUES
('Distribuidora Central', 15000.0, '12.345.678/0001-99', 'contato@distcentral.com', '69999990010', 6);

INSERT INTO pedido
(data_entrada_ped, prazo_entrega_ped, altura_ped, largura_ped, comprimento_ped, tara_ped, peso_ped, adendos_ped, status_ped, id_origem_loc_fk, id_destino_loc_fk, id_cli_fk, id_dist_fk)
VALUES
('2026-04-16', '2026-04-20', 1.0, 1.0, 1.0, 0.5, 2.0, 'Sem observações', 'Pendente', 1, 1, 1, 1),
('2026-04-16', '2026-04-21', 1.0, 1.0, 1.0, 0.5, 2.0, 'Sem observações', 'Pendente', 1, 1, 2, 1),
('2026-04-16', '2026-04-22', 1.0, 1.0, 1.0, 0.5, 2.0, 'Sem observações', 'Pendente', 1, 1, 3, 1),
('2026-04-16', '2026-04-23', 1.0, 1.0, 1.0, 0.5, 2.0, 'Sem observações', 'Pendente', 1, 1, 4, 1),
('2026-04-16', '2026-04-24', 1.0, 1.0, 1.0, 0.5, 2.0, 'Sem observações', 'Pendente', 1, 1, 5, 1);