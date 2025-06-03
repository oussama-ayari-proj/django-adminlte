create table if not exists ETB (
    code_ETB integer primary key,
    libelle_ETB text 
);

create table if not exists Pole (
    code_Pole integer primary key,
    libelle_Pole text 
);

create table if not exists UF (
    code_UF integer primary key,
    libelle_standard text ,
    code_ETB integer,
    code_Pole integer,
    type_UF text,
    Libelle_type_UF text ,
    type_activite text ,
    libelle_type_activite text 
    foreign key (code_ETB) references ETB(code_ETB),
    foreign key (code_Pole) references Pole(code_Pole)
);


create table if not exists Lits_2024(
    id integer primary key autoincrement,
    code_UF integer,
    semaine integer ,
    lits_installes integer ,
    lits_fermes_moyen float ,
    lits_fermes_max_prov float ,
    journees_fermeture float,
    foreign key (code_UF) references UF(code_UF)
);
create table if not exists EM (
    code_EM integer primary key,
    libelle_EM text 
);
create table if not exists sejours(
    id integer primary key autoincrement,
    num_sequence integer ,
    code_UF integer ,
    code_EM integer ,
    duree_sejour integer ,
    type_sejour text ,
    date_sortie date ,
    ghs integer ,
    sexe integer ,
    age_entree integer,
    foreign key (code_UF) references UF(code_UF),
    foreign key (code_EM) references EM(code_EM)
);


create table if not exists matrice_EM(
    id integer primary key autoincrement,
    code_EM integer ,
    code_UF integer ,
    num_Pole integer ,
    nb_rum integer,
    foreign key (code_EM) references EM(code_EM),
    foreign key (code_UF) references UF(code_UF),
)