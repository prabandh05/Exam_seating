import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Typography, Button, Spin, Tag } from 'antd';
import { useNavigate } from 'react-router-dom';
import { invigilatorAPI } from '../../api';

const { Title, Text } = Typography;

const InvigilatorDashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    invigilatorAPI.dashboard().then(res => setData(res.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div className="fade-in-up">
      <div className="page-header"><h2>My Duties</h2></div>
      
      {!data?.has_duties ? (
        <Card style={{ textAlign: 'center', padding: 50 }}>
          <Title level={3}>No Exam Duties Assigned</Title>
          <Text type="secondary">You will be notified when duties are assigned to you.</Text>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {data.upcoming_duties.map((duty: any) => (
            <Col xs={24} sm={12} md={8} key={duty.id}>
              <Card hoverable className="stat-card" style={{ borderColor: 'var(--primary)' }}
                    actions={[<Button type="primary" onClick={() => navigate(`/invigilator/duty/${duty.id}`)}>View Details</Button>]}>
                <Title level={4}>{duty.subject_name}</Title>
                <div style={{ marginBottom: 16 }}><Tag color="blue">{duty.exam_date}</Tag> <Tag color="orange">{duty.start_time} - {duty.end_time}</Tag></div>
                <Text strong>Hall:</Text> <Text>{duty.hall_number}</Text>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default InvigilatorDashboard;
