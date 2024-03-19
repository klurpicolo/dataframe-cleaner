import React from 'react'
import { Route, Routes } from 'react-router-dom'
import { ROUTES } from './RouterConfig';
import About from '../pages/About';
import Home from '../pages/Home'
import DataframeV1 from '../pages/DataframeV1';
import DataframeV2 from '../pages/DataframeV2';

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
            <Route exact path={ROUTES.Home} element={<RouteWithRole Element={Home} />}></Route>
            <Route exact path={ROUTES.About} element={<RouteWithRole Element={About} />}></Route>
            <Route exact path={ROUTES.DataframeV1} element={<RouteWithRole Element={DataframeV1} />}></Route>
            <Route exact path={ROUTES.DataframeV2} element={<RouteWithRole Element={DataframeV2} />}></Route>
        </Routes>
    </div>
  )
}

export default Router
