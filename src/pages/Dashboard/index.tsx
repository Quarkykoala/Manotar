import React from 'react';
import { Card, Row, Col, Typography } from 'antd';
import MainCard from 'ui-component/cards/MainCard';

const { Title } = Typography;

const Dashboard = () => {
  return (
    <MainCard title="Mental Health Dashboard">
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={8}>
          <Card title="Patient Overview">
            {/* Patient stats will go here */}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Mood Tracking">
            {/* Mood tracking chart will go here */}
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Session History">
            {/* Session history list will go here */}
          </Card>
        </Col>
        <Col xs={24}>
          <Card title="Chat Interface">
            {/* Chat component will go here */}
          </Card>
        </Col>
      </Row>
    </MainCard>
  );
};

export default Dashboard;
