import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Typography, Spin, Tag, Descriptions } from 'antd';
import { studentAPI } from '../../api';

const { Title, Text } = Typography;

const StudentDashboard: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    studentAPI.dashboard().then(res => setData(res.data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div className="fade-in-up">
      <div className="page-header"><h2>My Exams</h2></div>
      
      <Card style={{ marginBottom: 24 }}>
        <Descriptions title="Student Information" column={{ xxl: 4, xl: 3, lg: 3, md: 3, sm: 2, xs: 1 }}>
          <Descriptions.Item label="Name">{data?.student?.name}</Descriptions.Item>
          <Descriptions.Item label="Register No">{data?.student?.register_number}</Descriptions.Item>
          <Descriptions.Item label="Department">{data?.student?.department}</Descriptions.Item>
          <Descriptions.Item label="Semester">{data?.student?.semester}</Descriptions.Item>
          <Descriptions.Item label="Section">{data?.student?.section}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Title level={4}>Upcoming Exams & Seating</Title>
      {data?.upcoming_exams?.length === 0 ? (
        <Card style={{ textAlign: 'center', padding: 50 }}>
          <Text type="secondary">You have no upcoming exams scheduled.</Text>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {data?.upcoming_exams?.map((exam: any, i: number) => (
            <Col xs={24} sm={12} md={8} key={i}>
              <Card className="stat-card" style={{ borderColor: 'var(--primary)' }}>
                <Title level={4}>{exam.subject_name}</Title>
                <Text type="secondary">{exam.subject_code}</Text>
                <div style={{ margin: '16px 0' }}>
                  <Tag color="blue">{exam.exam_date}</Tag>
                  <Tag color="orange">{exam.start_time} - {exam.end_time}</Tag>
                </div>
                <div style={{ padding: 12, background: 'rgba(99, 102, 241, 0.1)', borderRadius: 8 }}>
                  <Row justify="space-between">
                    <Col><Text type="secondary">Hall</Text><br /><Text strong>{exam.hall_number}</Text></Col>
                    <Col><Text type="secondary">Seat</Text><br /><Text strong style={{ fontSize: 18, color: 'var(--primary)' }}>{exam.seat_number}</Text></Col>
                  </Row>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default StudentDashboard;
