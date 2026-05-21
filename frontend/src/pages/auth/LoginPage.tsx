import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Select, message, Spin } from 'antd';
import { UserOutlined, LockOutlined, SafetyCertificateOutlined } from '@ant-design/icons';
import { authAPI } from '../../api';
import { useAuth } from '../../context/AuthContext';

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const res = await authAPI.login(values);
      const data = res.data;
      login({
        user_id: data.user_id,
        name: data.name,
        role: data.role,
        token: data.access_token,
      });
      message.success(`Welcome, ${data.name}!`);
      navigate(`/${data.role}`);
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card fade-in-up">
        <div className="login-logo">
          <SafetyCertificateOutlined style={{ fontSize: 48, color: '#6366f1', marginBottom: 12 }} />
          <h1>Exam Seating</h1>
          <p>Management System</p>
        </div>

        <Form layout="vertical" onFinish={onFinish} size="large" requiredMark={false}>
          <Form.Item name="role" rules={[{ required: true, message: 'Select your role' }]}>
            <Select placeholder="Select Role" id="login-role-select">
              <Select.Option value="admin">🔑 Admin</Select.Option>
              <Select.Option value="invigilator">👨‍🏫 Invigilator</Select.Option>
              <Select.Option value="student">🎓 Student</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item name="username" rules={[{ required: true, message: 'Enter username / ID' }]}>
            <Input prefix={<UserOutlined />} placeholder="Username / Register No / ID" id="login-username" />
          </Form.Item>

          <Form.Item name="password" rules={[{ required: true, message: 'Enter password' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Password" id="login-password" />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary" htmlType="submit" block loading={loading}
              id="login-submit-btn"
              style={{
                height: 48, borderRadius: 12, fontWeight: 600,
                background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
                border: 'none',
              }}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 8 }}>
          <span style={{ color: '#64748b', fontSize: 12 }}>
            Default Admin: admin / admin123
          </span>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
