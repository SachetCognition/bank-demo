/**
 * Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
 * Use of this source code is governed by a BSD-style
 * license that can be found in the LICENSE file.
 */

import { Navigate, Outlet } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import { useEffect } from "react";
import { useCheckAuthQuery } from "../slices/usersApiSlice";
import { setCredentials, logout } from "../slices/authSlice";

const PrivateRoute = () => {
  const dispatch = useDispatch();
  const { userInfo, isLoading } = useSelector((state) => state.auth);
  const { data, error, isLoading: isCheckingAuth } = useCheckAuthQuery(undefined, {
    skip: userInfo !== null,
  });

  useEffect(() => {
    if (data) {
      dispatch(setCredentials(data));
    } else if (error) {
      dispatch(logout());
    }
  }, [data, error, dispatch]);

  if (isLoading || isCheckingAuth) {
    return <div>Loading...</div>;
  }

  return userInfo ? <Outlet /> : <Navigate to="/login" replace />;
};
export default PrivateRoute;
