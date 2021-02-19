--
-- PostgreSQL database dump
--

-- Dumped from database version 11.10
-- Dumped by pg_dump version 11.10

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

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: leak; Type: TABLE; Schema: public; Owner: credentialleakdb
--

CREATE TABLE public.leak (
    id integer NOT NULL,
    breach_ts timestamp with time zone,
    source_publish_ts timestamp with time zone,
    ingestion_ts timestamp with time zone NOT NULL,
    summary text NOT NULL,
    ticket_id text,
    reporter_name text,
    source_name text
);


ALTER TABLE public.leak OWNER TO credentialleakdb;

ALTER TABLE public.leak OWNER TO credentialleakdb;

--
-- Name: COLUMN leak.breach_ts; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak.breach_ts IS 'If known, the timestamp when the breach happened.';

--
-- Name: COLUMN leak.source_publish_ts; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak.source_publish_ts IS 'The timestamp according when the source (e.g. spycloud) published the data.';


--
-- Name: COLUMN leak.ingestion_ts; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak.ingestion_ts IS 'The timestamp when we ingested the data.';


--
-- Name: COLUMN leak.summary; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak.summary IS 'A short summary (slug) of the leak. Used for displaying it somewhere';


--
-- Name: COLUMN leak.reporter_name; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak.reporter_name IS 'The name of the reporter where we got the notification from. E.g. CERT-eu, Spycloud, etc... Who sent us the data?';


--
-- Name: COLUMN leak.source_name; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak.source_name IS 'The name of the source where this leak came from. Either the name of a collection or some other name.';


--
-- Name: leak_data; Type: TABLE; Schema: public; Owner: credentialleakdb
--

CREATE TABLE public.leak_data (
    id integer NOT NULL,
    leak_id integer NOT NULL,
    email text NOT NULL,
    password text NOT NULL,
    password_plain text,
    password_hashed text,
    hash_algo text,
    ticket_id text,
    email_verified boolean DEFAULT false,
    password_verified_ok boolean DEFAULT false,
    ip inet,
    domain text,
    browser text,
    malware_name text,
    infected_machine text,
	DG text NOT NULL
);


ALTER TABLE public.leak_data OWNER TO credentialleakdb;

--
-- Name: COLUMN leak_data.hash_algo; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak_data.hash_algo IS 'If we can determine the hashing algo and the password_hashed field is set';


--
-- Name: COLUMN leak_data.malware_name; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak_data.malware_name IS 'If the password was leaked via a credential stealer malware, then the malware name goes here.';

COMMENT ON COLUMN public.leak_data.infected_machine  IS 'The infected machine (some ID for the machine)';
COMMENT ON COLUMN public.leak_data.DG  IS 'The affected DG';


--
-- Name: COLUMN leak_data.password; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak_data.password IS 'Either the encrypted or unencrypted password. If the unencrypted password is available, that is what is going to be in this field.';


--
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
-- Name: leak_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: credentialleakdb
--

ALTER SEQUENCE public.leak_data_id_seq OWNED BY public.leak_data.id;


--
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
-- Name: leak_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: credentialleakdb
--

ALTER SEQUENCE public.leak_id_seq OWNED BY public.leak.id;


--
-- Name: leak id; Type: DEFAULT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak ALTER COLUMN id SET DEFAULT nextval('public.leak_id_seq'::regclass);


--
-- Name: leak_data id; Type: DEFAULT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak_data ALTER COLUMN id SET DEFAULT nextval('public.leak_data_id_seq'::regclass);


--
-- Data for Name: leak; Type: TABLE DATA; Schema: public; Owner: credentialleakdb
--

-- example:
-- COPY public.leak (id, breach_ts, source_publish_ts, ingestion_ts, summary, ticket_id, reporter_name, source_name) FROM stdin;
-- 1	2020-11-05 00:00:00+01	2020-11-05 00:00:00+01	2020-12-02 00:02:05.371812+01	Russian Password Stealer	\N	\N	\N
-- 2	2020-11-05 00:00:00+01	2020-11-05 00:00:00+01	2020-12-02 00:02:39.609522+01	Reincubate	\N	\N	\N
-- 3	2020-11-05 00:00:00+01	2020-11-05 00:00:00+01	2020-12-02 00:02:53.816163+01	Taurus Stealer	\N	\N	\N
-- 4	2020-11-05 00:00:00+01	2020-11-05 00:00:00+01	2020-12-02 00:03:34.302622+01	Azorult Botnet	\N	\N	\N
-- 5	2020-11-05 00:00:00+01	2020-11-05 00:00:00+01	2020-12-02 00:03:48.068866+01	Smoke Stealer	\N	\N	\N
-- 6	\N	\N	2021-02-14 01:45:04.36858+01	COMB	\N	\N	\N
-- \.

--
-- Data for Name: leak_data; Type: TABLE DATA; Schema: public; Owner: credentialleakdb
--

COPY public.leak_data (id, leak_id, email, password_hashed, hash_algo, password_plain, email_verified, password_verified_ok, ip, domain, browser, ticket_id, malware_name, password) FROM stdin;
\.


--
-- Name: leak_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: credentialleakdb
--

SELECT pg_catalog.setval('public.leak_data_id_seq', 1, true);


--
-- Name: leak_id_seq; Type: SEQUENCE SET; Schema: public; Owner: credentialleakdb
--
-- example:
SELECT pg_catalog.setval('public.leak_id_seq', 6, true);


--
-- Name: leak_data leak_data_pkey; Type: CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak_data
    ADD CONSTRAINT leak_data_pkey PRIMARY KEY (id);


--
-- Name: leak leak_pkey; Type: CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak
    ADD CONSTRAINT leak_pkey PRIMARY KEY (id);


--
-- Name: leak_data leak_data_leak_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak_data
    ADD CONSTRAINT leak_data_leak_id_fkey FOREIGN KEY (leak_id) REFERENCES public.leak(id);


--
-- PostgreSQL database dump complete
--

