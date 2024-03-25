import React from "react";
import { Route, Routes } from "react-router-dom";

import DataframeCleanerPage from "../pages/DataframeCleanerPage";

import { ROUTES } from "./RouterConfig";

const RouteWithRole = ({ Element }) => {
  return <Element />;
};

const Router = () => {
  return (
    <div>
      <Routes>
        <Route
          element={<RouteWithRole Element={DataframeCleanerPage} />}
          exact
          path={ROUTES.DataframeCleanerPage}
        />
      </Routes>
    </div>
  );
};

export default Router;
