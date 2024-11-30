import React from 'react';
import { Card, Row, Col } from 'antd';
import MainCard from 'ui-component/cards/MainCard';

const Analytics = () => {
  return (
    <MainCard title="Analytics Dashboard">
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card title="Sentiment Analysis">
            Coming soon...
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card title="Keyword Trends">
            Coming soon...
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card title="Usage Statistics">
            Coming soon...
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card title="Response Times">
            Coming soon...
          </Card>
        </Col>
      </Row>
    </MainCard>
  );
};

export default Analytics;
