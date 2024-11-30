import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';
import { styled } from '@mui/material/styles';

const MainContent = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  marginTop: '64px', // Height of the AppBar
  backgroundColor: '#f5f5f5',
  minHeight: '100vh'
}));

const Layout = () => {
  return (
    <Box sx={{ display: 'flex' }}>
      <MainContent>
        <Outlet />
      </MainContent>
    </Box>
  );
};

export default Layout;
