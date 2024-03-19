import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import api from "./api";

// Thunks
export const fetchRestCheck = createAsyncThunk("dataframe/fetch", async () => {
  const res = await api.get("/api/rest/dataframes/");
  return res.data;
});

export const createDataframe = createAsyncThunk("dataframe/create", async (dataframeData) => {
  const res = await api.post("/api/rest/dataframes/", dataframeData);
  return res.data;
});

// Reducer
export const restCheckReducer = createSlice({
  name: "dataframes",
  initialState: {},
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchRestCheck.pending, (state) => {
      state.data = {
        isLoading: true,
      };
    });
    builder.addCase(fetchRestCheck.fulfilled, (state, action) => {
      state.data = {
        isLoading: false,
        payload: action.payload,
      };
    });
    builder.addCase(fetchRestCheck.rejected, (state, action) => {
      state.data = {
        isLoading: false,
        error: action.error,
      };
    });
    builder.addCase(createDataframe.pending, (state) => {
      state.data = {
        status: "pending",
        payload: action.payload
      };
    });
    builder.addCase(createDataframe.fulfilled, (state, action) => {
      state.data = {
        status: "fulfilled",
        payload: action.payload
      };
    });
    builder.addCase(createDataframe.rejected, (state, action) => {
      state.data = {
        status: "rejected",
        payload: action.payload
      };
      // You might update the state accordingly here if necessary
    });
  },
}).reducer;
