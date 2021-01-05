--
-- PostgreSQL database dump
--

-- Dumped from database version 10.12 (Ubuntu 10.12-0ubuntu0.18.04.1)
-- Dumped by pg_dump version 10.12 (Ubuntu 10.12-0ubuntu0.18.04.1)

-- Started on 2020-12-08 16:18:51 CET

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2965 (class 1262 OID 17123)
-- Name: credentialleakdb; Type: DATABASE; Schema: -; Owner: credentialleakdb
--

CREATE DATABASE credentialleakdb WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';


ALTER DATABASE credentialleakdb OWNER TO credentialleakdb;

\connect credentialleakdb

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 1 (class 3079 OID 13041)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2967 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 203 (class 1259 OID 17214)
-- Name: collection; Type: TABLE; Schema: public; Owner: credentialleakdb
--

CREATE TABLE public.collection (
    id integer NOT NULL,
    ts timestamp with time zone,
    name character varying(1000)
);


ALTER TABLE public.collection OWNER TO credentialleakdb;

--
-- TOC entry 202 (class 1259 OID 17212)
-- Name: collection_id_seq; Type: SEQUENCE; Schema: public; Owner: credentialleakdb
--

CREATE SEQUENCE public.collection_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.collection_id_seq OWNER TO credentialleakdb;

--
-- TOC entry 2968 (class 0 OID 0)
-- Dependencies: 202
-- Name: collection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: credentialleakdb
--

ALTER SEQUENCE public.collection_id_seq OWNED BY public.collection.id;


--
-- TOC entry 199 (class 1259 OID 17182)
-- Name: leak; Type: TABLE; Schema: public; Owner: credentialleakdb
--

CREATE TABLE public.leak (
    id integer NOT NULL,
    breach_ts timestamp with time zone,
    source_publish_ts timestamp with time zone,
    ingestion_ts timestamp with time zone,
    leak_reporter_id integer,
    breach_title character varying(1000),
    leaked_website character varying(1000),
    jira_ticket_id character varying(32)
);


ALTER TABLE public.leak OWNER TO credentialleakdb;

--
-- TOC entry 204 (class 1259 OID 17224)
-- Name: leak2collection; Type: TABLE; Schema: public; Owner: credentialleakdb
--

CREATE TABLE public.leak2collection (
    collection_id integer,
    leak_id integer
);


ALTER TABLE public.leak2collection OWNER TO credentialleakdb;

--
-- TOC entry 201 (class 1259 OID 17198)
-- Name: leak_data; Type: TABLE; Schema: public; Owner: credentialleakdb
--

CREATE TABLE public.leak_data (
    id integer NOT NULL,
    leak_id integer,
    email character varying(1000),
    password_enc character varying(1000),
    password_unenc character varying(1000),
    email_verified boolean DEFAULT false,
    password_verified_ok boolean DEFAULT false,
    ip inet,
    domain character varying(1000),
    browser character varying(1000),
    jira_ticket_id character varying(32)
);


ALTER TABLE public.leak_data OWNER TO credentialleakdb;

--
-- TOC entry 200 (class 1259 OID 17196)
-- Name: leak_data_id_seq; Type: SEQUENCE; Schema: public; Owner: credentialleakdb
--

CREATE SEQUENCE public.leak_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.leak_data_id_seq OWNER TO credentialleakdb;

--
-- TOC entry 2969 (class 0 OID 0)
-- Dependencies: 200
-- Name: leak_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: credentialleakdb
--

ALTER SEQUENCE public.leak_data_id_seq OWNED BY public.leak_data.id;


--
-- TOC entry 198 (class 1259 OID 17180)
-- Name: leak_id_seq; Type: SEQUENCE; Schema: public; Owner: credentialleakdb
--

CREATE SEQUENCE public.leak_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.leak_id_seq OWNER TO credentialleakdb;

--
-- TOC entry 2970 (class 0 OID 0)
-- Dependencies: 198
-- Name: leak_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: credentialleakdb
--

ALTER SEQUENCE public.leak_id_seq OWNED BY public.leak.id;


--
-- TOC entry 197 (class 1259 OID 17171)
-- Name: leak_reporter; Type: TABLE; Schema: public; Owner: credentialleakdb
--

CREATE TABLE public.leak_reporter (
    id integer NOT NULL,
    name character varying(1000) NOT NULL
);


ALTER TABLE public.leak_reporter OWNER TO credentialleakdb;

--
-- TOC entry 196 (class 1259 OID 17169)
-- Name: leak_reporter_id_seq; Type: SEQUENCE; Schema: public; Owner: credentialleakdb
--

CREATE SEQUENCE public.leak_reporter_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.leak_reporter_id_seq OWNER TO credentialleakdb;

--
-- TOC entry 2971 (class 0 OID 0)
-- Dependencies: 196
-- Name: leak_reporter_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: credentialleakdb
--

ALTER SEQUENCE public.leak_reporter_id_seq OWNED BY public.leak_reporter.id;


--
-- TOC entry 2817 (class 2604 OID 17217)
-- Name: collection id; Type: DEFAULT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.collection ALTER COLUMN id SET DEFAULT nextval('public.collection_id_seq'::regclass);


--
-- TOC entry 2813 (class 2604 OID 17185)
-- Name: leak id; Type: DEFAULT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak ALTER COLUMN id SET DEFAULT nextval('public.leak_id_seq'::regclass);


--
-- TOC entry 2814 (class 2604 OID 17201)
-- Name: leak_data id; Type: DEFAULT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak_data ALTER COLUMN id SET DEFAULT nextval('public.leak_data_id_seq'::regclass);


--
-- TOC entry 2812 (class 2604 OID 17174)
-- Name: leak_reporter id; Type: DEFAULT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak_reporter ALTER COLUMN id SET DEFAULT nextval('public.leak_reporter_id_seq'::regclass);


--
-- TOC entry 2958 (class 0 OID 17214)
-- Dependencies: 203
-- Data for Name: collection; Type: TABLE DATA; Schema: public; Owner: credentialleakdb
--

COPY public.collection (id, ts, name) FROM stdin;
1	2020-10-02 00:00:00+02	Cit0Day
\.


--
-- TOC entry 2954 (class 0 OID 17182)
-- Dependencies: 199
-- Data for Name: leak; Type: TABLE DATA; Schema: public; Owner: credentialleakdb
--

COPY public.leak (id, breach_ts, source_publish_ts, ingestion_ts, leak_reporter_id, breach_title, leaked_website, jira_ticket_id) FROM stdin;
1	2020-11-05 00:00:00+01	2020-11-05 00:00:00+01	2020-12-02 00:02:05.371812+01	1	Russian Password Stealer	\N	\N
2	2020-11-05 00:00:00+01	2020-11-05 00:00:00+01	2020-12-02 00:02:39.609522+01	1	Reincubate	\N	\N
3	2020-11-05 00:00:00+01	2020-11-05 00:00:00+01	2020-12-02 00:02:53.816163+01	1	Taurus Stealer	\N	\N
4	2020-11-05 00:00:00+01	2020-11-05 00:00:00+01	2020-12-02 00:03:34.302622+01	1	Azorult Botnet	\N	\N
5	2020-11-05 00:00:00+01	2020-11-05 00:00:00+01	2020-12-02 00:03:48.068866+01	1	Smoke Stealer	\N	\N
\.



--
-- TOC entry 2952 (class 0 OID 17171)
-- Dependencies: 197
-- Data for Name: leak_reporter; Type: TABLE DATA; Schema: public; Owner: credentialleakdb
--

COPY public.leak_reporter (id, name) FROM stdin;
1	SpyCloud
2	HaveIBeenPwned
3	Cit0Day.in
\.


--
-- TOC entry 2972 (class 0 OID 0)
-- Dependencies: 202
-- Name: collection_id_seq; Type: SEQUENCE SET; Schema: public; Owner: credentialleakdb
--

SELECT pg_catalog.setval('public.collection_id_seq', 1, false);


--
-- TOC entry 2973 (class 0 OID 0)
-- Dependencies: 200
-- Name: leak_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: credentialleakdb
--

SELECT pg_catalog.setval('public.leak_data_id_seq', 1, true);


--
-- TOC entry 2974 (class 0 OID 0)
-- Dependencies: 198
-- Name: leak_id_seq; Type: SEQUENCE SET; Schema: public; Owner: credentialleakdb
--

SELECT pg_catalog.setval('public.leak_id_seq', 1, true);


--
-- TOC entry 2975 (class 0 OID 0)
-- Dependencies: 196
-- Name: leak_reporter_id_seq; Type: SEQUENCE SET; Schema: public; Owner: credentialleakdb
--

SELECT pg_catalog.setval('public.leak_reporter_id_seq', 1, false);


--
-- TOC entry 2825 (class 2606 OID 17222)
-- Name: collection collection_pkey; Type: CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.collection
    ADD CONSTRAINT collection_pkey PRIMARY KEY (id);


--
-- TOC entry 2823 (class 2606 OID 17206)
-- Name: leak_data leak_data_pkey; Type: CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak_data
    ADD CONSTRAINT leak_data_pkey PRIMARY KEY (id);


--
-- TOC entry 2821 (class 2606 OID 17190)
-- Name: leak leak_pkey; Type: CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak
    ADD CONSTRAINT leak_pkey PRIMARY KEY (id);


--
-- TOC entry 2819 (class 2606 OID 17179)
-- Name: leak_reporter leak_source_pkey; Type: CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak_reporter
    ADD CONSTRAINT leak_source_pkey PRIMARY KEY (id);


--
-- TOC entry 2828 (class 2606 OID 17227)
-- Name: leak2collection leak2collection_collection_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak2collection
    ADD CONSTRAINT leak2collection_collection_id_fkey FOREIGN KEY (collection_id) REFERENCES public.collection(id);


--
-- TOC entry 2829 (class 2606 OID 17232)
-- Name: leak2collection leak2collection_leak_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak2collection
    ADD CONSTRAINT leak2collection_leak_id_fkey FOREIGN KEY (leak_id) REFERENCES public.leak(id);


--
-- TOC entry 2827 (class 2606 OID 17207)
-- Name: leak_data leak_data_leak_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak_data
    ADD CONSTRAINT leak_data_leak_id_fkey FOREIGN KEY (leak_id) REFERENCES public.leak(id);


--
-- TOC entry 2826 (class 2606 OID 17191)
-- Name: leak leak_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak
    ADD CONSTRAINT leak_source_id_fkey FOREIGN KEY (leak_reporter_id) REFERENCES public.leak_reporter(id);


-- Completed on 2020-12-08 16:18:52 CET

--
-- PostgreSQL database dump complete
--