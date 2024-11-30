import React from 'react';
import { Card, CardProps } from 'antd';
import { styled } from '@mui/material/styles';

interface MainCardProps extends CardProps {
  children: React.ReactNode;
  title?: string;
}

const StyledCard = styled(Card)(({ theme }) => ({
  border: 'none',
  borderRadius: theme.shape.borderRadius,
  boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.15)',
  '.ant-card-head': {
    minHeight: 'auto',
    padding: '16px 24px',
    borderBottom: '1px solid #f0f0f0'
  },
  '.ant-card-body': {
    padding: '24px'
  }
}));

const MainCard: React.FC<MainCardProps> = ({ children, title, ...props }) => {
  return (
    <StyledCard title={title} {...props}>
      {children}
    </StyledCard>
  );
};

export default MainCard;
