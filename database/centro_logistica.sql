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
    foreign key (id_loc) references localidade(id_loc)
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