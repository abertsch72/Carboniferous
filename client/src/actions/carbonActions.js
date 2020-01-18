import axios from "axios";

import { REQUEST_CARBON, ITEMS_LOADING } from "./types.js";

export const requestCarbon = state => dispatch => {
  // use the app based on the input, set payload to the list of objects
  console.log("Submit Successful");
  axios
    .post("/api/carbon", state)
    .then(res => dispatch({ type: REQUEST_CARBON, payload: res.data }));
};

export const setItemsLoading = () => {
  return { type: ITEMS_LOADING };
};