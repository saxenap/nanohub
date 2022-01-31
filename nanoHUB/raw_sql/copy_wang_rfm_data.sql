-- auto-generated definition
use rfm_data;
create table if not exists rfm_data.MSI_status
(
  `index`                                             bigint null,
  `2019 List of Minority Serving Institutions (MSIs)` text   null,
  `Unnamed: 1`                                        text   null,
  `Unnamed: 2`                                        text   null,
  `Unnamed: 3`                                        text   null,
  `Unnamed: 4`                                        text   null
);

create index ix_MSI_status_index
  on rfm_data.MSI_status (`index`);

INSERT INTO rfm_data.MSI_status SELECT * FROM wang159_myrmekes.MSI_status;

create table if not exists rfm_data.benefactors
(
  id   int(10)      null,
  name varchar(255) null
  );

INSERT INTO rfm_data.benefactors SELECT * FROM wang159_myrmekes.benefactors;


create table if not exists rfm_data.cluster_class_info
(
  `index`  bigint   null,
  class_id bigint   null,
  start    datetime null,
  end      datetime null,
  lon      double   null,
  lat      double   null,
  size     bigint   null
);

create index ix_cluster_class_info_index
  on rfm_data.cluster_class_info (`index`);

INSERT INTO rfm_data.cluster_class_info SELECT * FROM wang159_myrmekes.cluster_class_info;

create table if not exists rfm_data.cluster_classtool_info
(
  `index`  bigint null,
  toolname text   null,
  class_id bigint null
);

create index ix_cluster_classtool_info_index
  on rfm_data.cluster_classtool_info (`index`);

INSERT INTO rfm_data.cluster_classtool_info SELECT * FROM wang159_myrmekes.cluster_classtool_info;

create table if not exists rfm_data.cluster_students_info
(
  `index`    bigint null,
  user       text   null,
  class_id   bigint null,
  parti_rate double null
);

create index ix_cluster_students_info_index
  on rfm_data.cluster_students_info (`index`);

INSERT INTO rfm_data.cluster_students_info SELECT * FROM wang159_myrmekes.cluster_students_info;


create table if not exists rfm_data.companies_email_domain
(
  `index`                     bigint null,
  name                        text   null,
  domain                      text   null,
  `year founded`              double null,
  industry                    text   null,
  `size range`                text   null,
  locality                    text   null,
  country                     text   null,
  `linkedin url`              text   null,
  `current employee estimate` bigint null,
  `total employee estimate`   bigint null
);

create index ix_companies_email_domain_index
  on rfm_data.companies_email_domain (`index`);


INSERT INTO rfm_data.companies_email_domain SELECT * FROM wang159_myrmekes.companies_email_domain;


create table if not exists rfm_data.detect_class_info
(
  `index`  bigint   null,
  class_id bigint   null,
  start    datetime null,
  end      datetime null,
  lon      double   null,
  lat      double   null,
  size     bigint   null
);

create index ix_detect_class_info_index
  on rfm_data.detect_class_info (`index`);

INSERT INTO rfm_data.detect_class_info SELECT * FROM wang159_myrmekes.detect_class_info;


create table if not exists rfm_data.donations
(
  id     int(10) null,
  bid    int(10) null,
  year   int(10) null,
  amount int(10) null
  );
INSERT INTO rfm_data.donations SELECT * FROM wang159_myrmekes.donations;


create table if not exists rfm_data.event_table
(
  start_datetime  datetime     null,
  end_datetime    datetime     null,
  timeline_domain varchar(100) null,
  timeline_label  varchar(100) null,
  id_nanohub      varchar(100) null,
  id_email        varchar(100) null,
  id_hubspot      varchar(200) null
  );
INSERT INTO rfm_data.event_table SELECT * FROM wang159_myrmekes.event_table;

create table if not exists rfm_data.institution_characteristics
(
  `index`  bigint null,
  UNITID   bigint null,
  INSTNM   text   null,
  IALIAS   text   null,
  ADDR     text   null,
  CITY     text   null,
  STABBR   text   null,
  ZIP      text   null,
  FIPS     bigint null,
  OBEREG   bigint null,
  CHFNM    text   null,
  CHFTITLE text   null,
  GENTELE  text   null,
  EIN      bigint null,
  DUNS     text   null,
  OPEID    bigint null,
  OPEFLAG  bigint null,
  WEBADDR  text   null,
  ADMINURL text   null,
  FAIDURL  text   null,
  APPLURL  text   null,
  NPRICURL text   null,
  VETURL   text   null,
  ATHURL   text   null,
  DISAURL  text   null,
  SECTOR   bigint null,
  ICLEVEL  bigint null,
  CONTROL  bigint null,
  HLOFFER  bigint null,
  UGOFFER  bigint null,
  GROFFER  bigint null,
  HDEGOFR1 bigint null,
  DEGGRANT bigint null,
  HBCU     bigint null,
  HOSPITAL bigint null,
  MEDICAL  bigint null,
  TRIBAL   bigint null,
  LOCALE   bigint null,
  OPENPUBL bigint null,
  ACT      text   null,
  NEWID    bigint null,
  DEATHYR  bigint null,
  CLOSEDAT text   null,
  CYACTIVE bigint null,
  POSTSEC  bigint null,
  PSEFLAG  bigint null,
  PSET4FLG bigint null,
  RPTMTH   bigint null,
  INSTCAT  bigint null,
  C18BASIC bigint null,
  C18IPUG  bigint null,
  C18IPGRD bigint null,
  C18UGPRF bigint null,
  C18ENPRF bigint null,
  C18SZSET bigint null,
  C15BASIC bigint null,
  CCBASIC  bigint null,
  CARNEGIE bigint null,
  LANDGRNT bigint null,
  INSTSIZE bigint null,
  F1SYSTYP bigint null,
  F1SYSNAM text   null,
  F1SYSCOD bigint null,
  CBSA     bigint null,
  CBSATYPE bigint null,
  CSA      bigint null,
  NECTA    bigint null,
  COUNTYCD bigint null,
  COUNTYNM text   null,
  CNGDSTCD bigint null,
  LONGITUD double null,
  LATITUDE double null,
  DFRCGID  bigint null,
  DFRCUSCG bigint null
);

create index ix_institution_characteristics_index
  on rfm_data.institution_characteristics (`index`);

INSERT INTO rfm_data.institution_characteristics SELECT * FROM wang159_myrmekes.institution_characteristics;


create table if not exists rfm_data.institution_classification
(
  `index`        bigint null,
  UNITID         bigint null,
  NAME           text   null,
  CITY           text   null,
  STABBR         text   null,
  CC2000         bigint null,
  BASIC2005      bigint null,
  BASIC2010      bigint null,
  BASIC2015      bigint null,
  BASIC2018      bigint null,
  IPUG2018       bigint null,
  IPGRAD2018     bigint null,
  ENRPROFILE2018 bigint null,
  UGPROFILE2018  bigint null,
  SIZESET2018    bigint null,
  CCE2015        bigint null,
  OBEREG         bigint null,
  SECTOR         bigint null,
  ICLEVEL        bigint null,
  CONTROL        bigint null,
  LOCALE         bigint null,
  LANDGRNT       bigint null,
  MEDICAL        bigint null,
  HBCU           bigint null,
  TRIBAL         bigint null,
  HSI            bigint null,
  MSI            bigint null,
  WOMENS         bigint null,
  COPLAC         bigint null,
  CUSU           bigint null,
  CUMU           bigint null,
  ASSOCDEG       bigint null,
  BACCDEG        bigint null,
  MASTDEG        bigint null,
  DOCRSDEG       bigint null,
  DOCPPDEG       bigint null,
  DOCOTHDEG      bigint null,
  TOTDEG         bigint null,
  `S&ER&D`       text   null,
  `NONS&ER&D`    text   null,
  PDNFRSTAFF     text   null,
  FACNUM         text   null,
  HUM_RSD        text   null,
  SOCSC_RSD      text   null,
  STEM_RSD       text   null,
  OTHER_RSD      text   null,
  `DRSA&S`       bigint null,
  DRSPROF        bigint null,
  `OGRDA&S`      bigint null,
  OGRDPROF       bigint null,
  `A&SBADEG`     bigint null,
  PROFBADEG      bigint null,
  ASC1C2TRNS     bigint null,
  ASC1C2CRTC     bigint null,
  FALLENR16      double null,
  ANENR1617      double null,
  FALLENR17      bigint null,
  FALLFTE17      double null,
  UGTENR17       bigint null,
  GRTENR17       bigint null,
  UGDSFTF17      double null,
  UGDSPTF17      double null,
  UGNDFT17       double null,
  UGNDPT17       double null,
  GRFTF17        double null,
  GRPTF17        double null,
  UGN1STTMFT17   double null,
  UGN1STTMPT17   double null,
  UGNTRFT17      double null,
  UGNTRPT17      double null,
  FAITHFLAG      bigint null,
  OTHSFFLAG      bigint null,
  NUMCIP2        bigint null,
  LRGSTCIP2      bigint null,
  PCTLRGST       double null,
  UGCIP4PR       bigint null,
  GRCIP4PR       bigint null,
  COEXPR         bigint null,
  PCTCOEX        double null,
  DOCRESFLAG     bigint null,
  MAXGPEDUC      bigint null,
  MAXGPBUS       bigint null,
  MAXGPOTH       bigint null,
  NGCIP2PXDR     bigint null,
  NGCIP2DR       bigint null,
  ROOMS          bigint null,
  ACTCAT         bigint null,
  NSAT           bigint null,
  NACT           bigint null,
  NSATACT        bigint null,
  SATV25         double null,
  SATM25         double null,
  SATCMB25       double null,
  SATACTEQ25     double null,
  ACTCMP25       double null,
  ACTFINAL       double null,
  Unnamed95      double null,
  Unnamed96      double null
);

create index ix_institution_classification_index
  on rfm_data.institution_classification (`index`);

INSERT INTO rfm_data.institution_classification SELECT * FROM wang159_myrmekes.institution_classification;


create table if not exists rfm_data.institution_classification_labels
(
  `index`  bigint null,
  Variable text   null,
  Value    double null,
  Label    text   null
);

create index ix_institution_classification_labels_index
  on rfm_data.institution_classification_labels (`index`);

INSERT INTO rfm_data.institution_classification_labels SELECT * FROM wang159_myrmekes.institution_classification_labels;



create table if not exists rfm_data.institution_variable_labels
(
  `index`  bigint null,
  Variable text   null,
  Label    text   null,
  Source   text   null
);

create index ix_institution_variable_labels_index
  on rfm_data.institution_variable_labels (`index`);

INSERT INTO rfm_data.institution_variable_labels SELECT * FROM wang159_myrmekes.institution_variable_labels;


create table if not exists rfm_data.issue_invalid_urls
(
  `index`     bigint null,
  resource_ID text   null,
  href        text   null,
  href_text   text   null,
  status      text   null
);

create index ix_issue_invalid_urls_index
  on rfm_data.issue_invalid_urls (`index`);

INSERT INTO rfm_data.issue_invalid_urls SELECT * FROM wang159_myrmekes.issue_invalid_urls;


create table if not exists rfm_data.temp_champ
(
  uid varchar(255) not null
  );

INSERT INTO rfm_data.temp_champ SELECT * FROM wang159_myrmekes.temp_champ;



create table if not exists rfm_data.us_news_rankings
(
  `index`                 bigint null,
  UNITID                  bigint null,
  INSTNM                  text   null,
  WEBADDR                 text   null,
  usn_gr_ae               double null,
  usn_gr_EE               double null,
  chem_gr_anal            double null,
  chem_gr_inorg           double null,
  chem_gr_phy             double null,
  chem_gr_bio             text   null,
  chem_gr_org             text   null,
  chem_gr_theo            double null,
  phys_gr_atom            double null,
  phys_gr_quan            double null,
  usn_ug_CE_w_doct        double null,
  usn_ug_ME_w_doct        double null,
  usn_ug_ME_no_doct       double null,
  usn_ug_ChE_w_doct       double null,
  usn_ug_ChE_no_doct      double null,
  usn_ug_IE_w_doct        double null,
  usn_ug_IE_no_doct       double null,
  usn_ug_MSE_w_doct       double null,
  usn_ug_eng_no_doctorate double null,
  usn_gr_IE               double null,
  usn_gr_mse              double null,
  usn_gr_me               double null,
  usn_gr_ce               double null,
  usn_ug_eng_w_doct       double null,
  usn_ug_EE_no_doct       double null,
  usn_ug_EE_w_doct        double null,
  phys_gr_con             double null,
  usn_gr_eng              text   null,
  usn_natl_publ           double null,
  usn_natl                text   null,
  `Unnamed: 33`           text   null
);

create index ix_us_news_rankings_index
  on rfm_data.us_news_rankings (`index`);

INSERT INTO rfm_data.us_news_rankings SELECT * FROM wang159_myrmekes.us_news_rankings;


create table if not exists rfm_data.user_activity_blocks
(
  `index`      bigint   null,
  user         text     null,
  tool         text     null,
  start        datetime null,
  end          datetime null,
  ip           text     null,
  lon          double   null,
  lat          double   null,
  cluster      bigint   null,
  scanned_date datetime null
);

create index ix_user_activity_blocks_index
  on rfm_data.user_activity_blocks (`index`);

INSERT INTO rfm_data.user_activity_blocks SELECT * FROM wang159_myrmekes.user_activity_blocks;


# DROP TABLE IF EXISTS rfm_data.MSI_status;
# DROP TABLE IF EXISTS rfm_data.benefactors;
# DROP TABLE IF EXISTS rfm_data.cluster_class_info;
# DROP TABLE IF EXISTS rfm_data.cluster_classtool_info;
# DROP TABLE IF EXISTS rfm_data.cluster_students_info;
# DROP TABLE IF EXISTS rfm_data.companies_email_domain;
# DROP TABLE IF EXISTS rfm_data.detect_class_info;
# DROP TABLE IF EXISTS rfm_data.donations;
# DROP TABLE IF EXISTS rfm_data.event_table;
# DROP TABLE IF EXISTS rfm_data.institution_characteristics;
# DROP TABLE IF EXISTS rfm_data.institution_classification;
# DROP TABLE IF EXISTS rfm_data.institution_classification_labels;
# DROP TABLE IF EXISTS rfm_data.institution_variable_labels;
# DROP TABLE IF EXISTS rfm_data.issue_invalid_urls;
# DROP TABLE IF EXISTS rfm_data.temp_champ;
# DROP TABLE IF EXISTS rfm_data.us_news_rankings;
# DROP TABLE IF EXISTS rfm_data.user_activity_blocks;


# INSERT INTO rfm_data.cluster_class_info SELECT * FROM wang159_myrmekes.cluster_class_info;
# INSERT INTO rfm_data.cluster_classtool_info SELECT * FROM wang159_myrmekes.cluster_classtool_info;
# INSERT INTO rfm_data.cluster_students_info SELECT * FROM wang159_myrmekes.cluster_students_info;
# INSERT INTO rfm_data.temp_champ SELECT * FROM wang159_myrmekes.temp_champ;
# INSERT INTO rfm_data.issue_invalid_urls SELECT * FROM wang159_myrmekes.issue_invalid_urls;
# INSERT INTO rfm_data.temp_champ SELECT * FROM wang159_myrmekes.temp_champ;
# INSERT INTO rfm_data.us_news_rankings SELECT * FROM wang159_myrmekes.us_news_rankings;
# INSERT INTO rfm_data.user_activity_blocks SELECT * FROM wang159_myrmekes.user_activity_blocks;

# truncate rfm_data.cluster_class_info;
# truncate rfm_data.cluster_classtool_info;
# truncate rfm_data.cluster_students_info;