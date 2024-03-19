import React from 'react'
import { Route, Routes } from 'react-router-dom'
import { ROUTES } from './RouterConfig';
import About from '../pages/About';
import Home from '../pages/Home'
import DataFrameDisplay from '../pages/DataFrameDisplay';

const RouteWithRole = ({ Element }) => {
  return (
    <>
      <Element/>
    </>
  );
}

const Router = () => {
  return (
    <div>
        <Routes>
            <Route exact path={ROUTES.HomeKlur} element={<RouteWithRole Element={Home} />}></Route>
            <Route exact path={ROUTES.About} element={<RouteWithRole Element={About} />}></Route>
            <Route exact path={ROUTES.DataframeV1} element={<RouteWithRole Element={DataFrameDisplay} />}></Route>
        </Routes>
    </div>
  )
}

export default Router
