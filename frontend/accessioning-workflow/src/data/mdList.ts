import type { MdEntry } from '../types/index.ts';

/**
 * Pathologist lookup table — mirrors data/md_list.py.
 * Sorted alphabetically by last name.
 * Display name format: "First [Middle] Last"
 */
export const MD_LIST: MdEntry[] = [
  { last: 'Asgari',        first: 'Masoud',     middle: null,    display_name: 'Masoud Asgari' },
  { last: 'Babaidorabad',  first: 'Nasim',      middle: null,    display_name: 'Nasim Babaidorabad' },
  { last: 'Behl',          first: 'Preeti',     middle: null,    display_name: 'Preeti Behl' },
  { last: 'Campos',        first: 'Marite A.',  middle: null,    display_name: 'Marite A. Campos' },
  { last: 'Chang',         first: 'Harvey',     middle: null,    display_name: 'Harvey Chang' },
  { last: 'Chaudhari',     first: 'Prakash',    middle: null,    display_name: 'Prakash Chaudhari' },
  { last: 'Connolly',      first: 'Stephen G.', middle: null,    display_name: 'Stephen G. Connolly' },
  { last: 'Costa',         first: 'Michael',    middle: null,    display_name: 'Michael Costa' },
  { last: 'Cui',           first: 'Shijun',     middle: null,    display_name: 'Shijun Cui' },
  { last: 'Emery',         first: 'Shawn',      middle: null,    display_name: 'Shawn Emery' },
  { last: 'Fogel',         first: 'Steven',     middle: null,    display_name: 'Steven Fogel' },
  { last: 'Hardee',        first: 'Steven',     middle: null,    display_name: 'Steven Hardee' },
  { last: 'Hare',          first: 'Donovan',    middle: 'Robert', display_name: 'Donovan Robert Hare' },
  { last: 'Haydel',        first: 'Dana',       middle: null,    display_name: 'Dana Haydel' },
  { last: 'Kaabipour',     first: 'Emad',       middle: null,    display_name: 'Emad Kaabipour' },
  { last: 'Land',          first: 'Terry',      middle: null,    display_name: 'Terry Land' },
  { last: 'Limjoco',       first: 'Teresa',     middle: null,    display_name: 'Teresa Limjoco' },
  { last: 'Nguyen',        first: 'Tuan',       middle: null,    display_name: 'Tuan Nguyen' },
  { last: 'Ohan',          first: 'Hovsep',     middle: null,    display_name: 'Hovsep Ohan' },
  { last: 'Perez-Valles',  first: 'Christy',    middle: null,    display_name: 'Christy Perez-Valles' },
  { last: 'Rodgers',       first: 'Melissa',    middle: null,    display_name: 'Melissa Rodgers' },
  { last: 'Setarehshenas', first: 'Roya',       middle: null,    display_name: 'Roya Setarehshenas' },
  { last: 'Shaker',        first: 'Nada',       middle: null,    display_name: 'Nada Shaker' },
  { last: 'Starshak',      first: 'Phillip E.', middle: null,    display_name: 'Phillip E. Starshak' },
  { last: 'Victorio',      first: 'Anthony R.', middle: null,    display_name: 'Anthony R. Victorio' },
  { last: 'Wassimi',       first: 'Spogmai',    middle: null,    display_name: 'Spogmai Wassimi' },
  { last: 'Watson',        first: 'Ashley',     middle: null,    display_name: 'Ashley Watson' },
];

/** Bone-marrow-eligible pathologists only (3 entries). */
export const BONE_MARROW_ELIGIBLE: MdEntry[] = MD_LIST.filter(
  (e) => e.last === 'Babaidorabad' || e.last === 'Hardee' || e.last === 'Starshak'
);
