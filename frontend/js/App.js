import * as Sentry from "@sentry/react";
import React from "react";
import { Provider } from "react-redux";
import configureStore from "./store";

import { BrowserRouter } from 'react-router-dom';
import Router from './routes/Router';

const store = configureStore({});
const App = () => (
  <Sentry.ErrorBoundary fallback={<p>An error has occurred</p>}>
    <Provider store={store}>
      <BrowserRouter>
        <Router/>
      </BrowserRouter>
    </Provider>
  </Sentry.ErrorBoundary>
);

export default App;
