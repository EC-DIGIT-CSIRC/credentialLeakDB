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
    dg text NOT NULL,
    count_seen integer DEFAULT 1
);


ALTER TABLE public.leak_data OWNER TO credentialleakdb;

--
-- Name: COLUMN leak_data.password; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak_data.password IS 'Either the encrypted or unencrypted password. If the unencrypted password is available, that is what is going to be in this field.';


--
-- Name: COLUMN leak_data.hash_algo; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak_data.hash_algo IS 'If we can determine the hashing algo and the password_hashed field is set';


--
-- Name: COLUMN leak_data.malware_name; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak_data.malware_name IS 'If the password was leaked via a credential stealer malware, then the malware name goes here.';


--
-- Name: COLUMN leak_data.infected_machine; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak_data.infected_machine IS 'The infected machine (some ID for the machine)';


--
-- Name: COLUMN leak_data.dg; Type: COMMENT; Schema: public; Owner: credentialleakdb
--

COMMENT ON COLUMN public.leak_data.dg IS 'The affected DG';


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


SELECT pg_catalog.setval('public.leak_id_seq', 1, true);
--
-- Data for Name: leak; Type: TABLE DATA; Schema: public; Owner: credentialleakdb
--

COPY public.leak (id, breach_ts, source_publish_ts, ingestion_ts, summary, ticket_id, reporter_name, source_name) FROM stdin;
1	2021-03-08 13:58:41.179+01	2021-03-08 13:58:41.179+01	2021-03-06 23:40:20.116348+01	CIT0DAY-2	CSIRC-99999	aaron	HaveIBennPwned
2	2021-03-06 23:40:47.266962+01	2021-03-06 23:40:47.266962+01	2021-03-06 23:40:47.266962+01	COMB	CSIRC-102	aaron	independen research
3	2021-03-06 23:41:10.245034+01	2021-03-06 23:41:10.245034+01	2021-03-06 23:41:10.245034+01	cit0day	CSIRC-103	aaron	HaveIBeenPwned
\.


--
-- Data for Name: leak_data; Type: TABLE DATA; Schema: public; Owner: credentialleakdb
--

SELECT pg_catalog.setval('public.leak_data_id_seq', 1, true);

COPY public.leak_data (id, leak_id, email, password, password_plain, password_hashed, hash_algo, ticket_id, email_verified, password_verified_ok, ip, domain, browser, malware_name, infected_machine, dg, count_seen) FROM stdin;
1	1	aaron@example.com	12345	12345	\N	\N	CISRC-199	f	f	1.2.3.4	example.com	Google Chrome	\N	local_laptop	DIGIT	25
2	1	sarah@example.com	123456	123456	\N	\N	CISRC-199	f	f	1.2.3.5	example.com	Firefox	\N	sarahs_laptop	DIGIT	8
3	1	ben@example.com	ohk7do7gil6O	ohk7do7gil6O	4aa7985dad6e1f02238c2e2afc521c4d3dd30650656cd07bf0b7cfd3cd1190b7	sha256	CISRC-199	f	f	1.2.3.5	example.com	Firefox	\N	WORKSTATION	DIGIT	8
4	1	david@example.com	24b3f998468a9da4105e6c78f5444532cde99d53c011715754194c3b4f3e37b4	\N	24b3f998468a9da4105e6c78f5444532cde99d53c011715754194c3b4f3e37b4	sha256	CISRC-199	f	f	8.8.8.8	example.com	Firefox	\N	Macbook Pro	DIGIT	8
5	2	lauri@example.com	Vie5kuuwiroo	Vie5kuuwiroo	\N	\N	CISRC-200	t	t	9.9.9.9	example.com	Firefox	\N	Raspberry PI 3+	DIGIT	8
6	2	natasha@example.com	1235kuuwiroo	1235kuuwiroo	\N	\N	CISRC-201	t	t	9.9.9.9	example.com	Firefox	\N	Raspberry PI 3+	DIGIT	2
\.


--
-- Name: leak_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: credentialleakdb
--

SELECT pg_catalog.setval('public.leak_data_id_seq', 7, true);


--
-- Name: leak_id_seq; Type: SEQUENCE SET; Schema: public; Owner: credentialleakdb
--

SELECT pg_catalog.setval('public.leak_id_seq', 4, true);


--
-- Name: leak_data constr_unique_leak_data_leak_id_email_password_domain; Type: CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak_data
    ADD CONSTRAINT constr_unique_leak_data_leak_id_email_password_domain UNIQUE (leak_id, email, password, domain);


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
-- Name: idx_leak_data_dg; Type: INDEX; Schema: public; Owner: credentialleakdb
--

CREATE INDEX idx_leak_data_dg ON public.leak_data USING btree (dg);


--
-- Name: idx_leak_data_email; Type: INDEX; Schema: public; Owner: credentialleakdb
--

CREATE INDEX idx_leak_data_email ON public.leak_data USING btree (upper(email));


--
-- Name: idx_leak_data_email_password_machine; Type: INDEX; Schema: public; Owner: credentialleakdb
--

CREATE INDEX idx_leak_data_email_password_machine ON public.leak_data USING btree (email, password, infected_machine);


--
-- Name: idx_leak_data_malware_name; Type: INDEX; Schema: public; Owner: credentialleakdb
--

CREATE INDEX idx_leak_data_malware_name ON public.leak_data USING btree (malware_name);


--
-- Name: idx_leak_data_unique_leak_id_email_password_domain; Type: INDEX; Schema: public; Owner: credentialleakdb
--

CREATE UNIQUE INDEX idx_leak_data_unique_leak_id_email_password_domain ON public.leak_data USING btree (leak_id, email, password, domain);


--
-- Name: leak_data leak_data_leak_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: credentialleakdb
--

ALTER TABLE ONLY public.leak_data
    ADD CONSTRAINT leak_data_leak_id_fkey FOREIGN KEY (leak_id) REFERENCES public.leak(id);


--
-- PostgreSQL database dump complete
--

