/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import { Container } from "react-bootstrap";
import { Outlet } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Header from "./components/Header";
import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { useCheckAuthQuery } from "./slices/usersApiSlice";
import { setCredentials, setLoading } from "./slices/authSlice";

const App = () => {
  const dispatch = useDispatch();
  const { data, error, isLoading } = useCheckAuthQuery();

  useEffect(() => {
    if (data) {
      dispatch(setCredentials(data));
    } else if (error || !isLoading) {
      dispatch(setLoading(false));
    }
  }, [data, error, isLoading, dispatch]);

  return (
    <div>
      <Header />
      <ToastContainer />
      <Container className="my-2">
        <Outlet />
      </Container>
    </div>
  );
};

export default App;
