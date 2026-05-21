import React, { useEffect, useState } from 'react';
import { List, Card, Typography, Spin, Badge } from 'antd';
import { studentAPI } from '../../api';

const { Text } = Typography;

const StudentNotifications: React.FC = () => {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch = () => {
    studentAPI.getNotifications().then(res => setNotifications(res.data.notifications))
      .catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { fetch(); }, []);

  return (
    <div className="fade-in-up">
      <div className="page-header"><h2>Notifications</h2></div>
      <Card loading={loading}>
        <List
          itemLayout="horizontal"
          dataSource={notifications}
          renderItem={(item: any) => (
            <List.Item>
              <List.Item.Meta
                title={<Badge dot={!item.is_read}>{item.title}</Badge>}
                description={
                  <div>
                    <Text>{item.message}</Text><br />
                    <Text type="secondary" style={{ fontSize: 12 }}>{new Date(item.created_at).toLocaleString()}</Text>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default StudentNotifications;
