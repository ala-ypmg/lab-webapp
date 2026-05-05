import { createContext, useContext } from 'react';

/** Increments each time a submit attempt ends with validation errors. */
export const SubmitKeyContext = createContext(0);
export const useSubmitKey = () => useContext(SubmitKeyContext);
