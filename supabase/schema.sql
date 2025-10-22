-- Casa&Più Database Schema
-- PostgreSQL/Supabase

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    supabase_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create assets table (properties and vehicles)
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('property', 'vehicle')),
    name VARCHAR(255) NOT NULL,
    details_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE SET NULL,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    due_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'overdue')),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN ('imu', 'bollo', 'assicurazione', 'revisione', 'bolletta', 'altro')),
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    message TEXT NOT NULL,
    notified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create automations table
CREATE TABLE IF NOT EXISTS automations (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    imu_calc BOOLEAN DEFAULT FALSE,
    f24_gen BOOLEAN DEFAULT FALSE,
    ocr BOOLEAN DEFAULT FALSE,
    ai_suggestions BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(asset_id)
);

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    file_url TEXT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    parsed_data_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_assets_user_id ON assets(user_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);
CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_asset_id ON expenses(asset_id);
CREATE INDEX IF NOT EXISTS idx_expenses_status ON expenses(status);
CREATE INDEX IF NOT EXISTS idx_expenses_due_date ON expenses(due_date);
CREATE INDEX IF NOT EXISTS idx_reminders_asset_id ON reminders(asset_id);
CREATE INDEX IF NOT EXISTS idx_reminders_date ON reminders(date);
CREATE INDEX IF NOT EXISTS idx_reminders_notified ON reminders(notified);
CREATE INDEX IF NOT EXISTS idx_automations_asset_id ON automations(asset_id);
CREATE INDEX IF NOT EXISTS idx_documents_asset_id ON documents(asset_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assets_updated_at BEFORE UPDATE ON assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_expenses_updated_at BEFORE UPDATE ON expenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_automations_updated_at BEFORE UPDATE ON automations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) for Supabase
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE automations ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create policies for users
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = supabase_id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = supabase_id);

-- Create policies for assets
CREATE POLICY "Users can view own assets" ON assets
    FOR SELECT USING (user_id IN (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

CREATE POLICY "Users can create own assets" ON assets
    FOR INSERT WITH CHECK (user_id IN (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

CREATE POLICY "Users can update own assets" ON assets
    FOR UPDATE USING (user_id IN (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

CREATE POLICY "Users can delete own assets" ON assets
    FOR DELETE USING (user_id IN (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

-- Create policies for expenses
CREATE POLICY "Users can view own expenses" ON expenses
    FOR SELECT USING (user_id IN (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

CREATE POLICY "Users can create own expenses" ON expenses
    FOR INSERT WITH CHECK (user_id IN (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

CREATE POLICY "Users can update own expenses" ON expenses
    FOR UPDATE USING (user_id IN (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

CREATE POLICY "Users can delete own expenses" ON expenses
    FOR DELETE USING (user_id IN (SELECT id FROM users WHERE supabase_id = auth.uid()::text));

-- Create policies for reminders
CREATE POLICY "Users can view own reminders" ON reminders
    FOR SELECT USING (asset_id IN (
        SELECT id FROM assets WHERE user_id IN (
            SELECT id FROM users WHERE supabase_id = auth.uid()::text
        )
    ));

CREATE POLICY "Users can create own reminders" ON reminders
    FOR INSERT WITH CHECK (asset_id IN (
        SELECT id FROM assets WHERE user_id IN (
            SELECT id FROM users WHERE supabase_id = auth.uid()::text
        )
    ));

-- Create policies for automations
CREATE POLICY "Users can view own automations" ON automations
    FOR SELECT USING (asset_id IN (
        SELECT id FROM assets WHERE user_id IN (
            SELECT id FROM users WHERE supabase_id = auth.uid()::text
        )
    ));

CREATE POLICY "Users can create own automations" ON automations
    FOR INSERT WITH CHECK (asset_id IN (
        SELECT id FROM assets WHERE user_id IN (
            SELECT id FROM users WHERE supabase_id = auth.uid()::text
        )
    ));

CREATE POLICY "Users can update own automations" ON automations
    FOR UPDATE USING (asset_id IN (
        SELECT id FROM assets WHERE user_id IN (
            SELECT id FROM users WHERE supabase_id = auth.uid()::text
        )
    ));

-- Create policies for documents
CREATE POLICY "Users can view own documents" ON documents
    FOR SELECT USING (asset_id IN (
        SELECT id FROM assets WHERE user_id IN (
            SELECT id FROM users WHERE supabase_id = auth.uid()::text
        )
    ));

CREATE POLICY "Users can create own documents" ON documents
    FOR INSERT WITH CHECK (asset_id IN (
        SELECT id FROM assets WHERE user_id IN (
            SELECT id FROM users WHERE supabase_id = auth.uid()::text
        )
    ));

-- Insert sample data (optional, for testing)
-- Uncomment to add test data

/*
INSERT INTO users (email, name, supabase_id) VALUES
    ('test@example.com', 'Test User', 'test-uuid-123');

INSERT INTO assets (user_id, type, name, details_json) VALUES
    (1, 'property', 'Casa Via Roma 123', '{"indirizzo": "Via Roma 123", "comune": "Milano", "categoria_catastale": "A/2", "rendita": 1000.00, "prima_casa": true}'::jsonb),
    (1, 'vehicle', 'Fiat Panda', '{"targa": "AB123CD", "marca": "Fiat", "modello": "Panda", "anno": 2020, "tipo": "auto"}'::jsonb);

INSERT INTO expenses (user_id, asset_id, category, amount, due_date, status, description) VALUES
    (1, 1, 'imu', 500.00, '2024-06-16', 'pending', 'Primo acconto IMU 2024'),
    (1, 2, 'bollo', 180.00, '2024-12-31', 'pending', 'Bollo auto 2024');

INSERT INTO automations (asset_id, imu_calc, f24_gen, ai_suggestions) VALUES
    (1, true, true, true),
    (2, false, false, true);
*/

-- Create a view for asset statistics
CREATE OR REPLACE VIEW asset_statistics AS
SELECT 
    u.id as user_id,
    u.name as user_name,
    COUNT(DISTINCT a.id) as total_assets,
    COUNT(DISTINCT CASE WHEN a.type = 'property' THEN a.id END) as properties_count,
    COUNT(DISTINCT CASE WHEN a.type = 'vehicle' THEN a.id END) as vehicles_count,
    COUNT(DISTINCT e.id) as total_expenses,
    COALESCE(SUM(e.amount), 0) as total_expense_amount,
    COUNT(DISTINCT CASE WHEN e.status = 'pending' THEN e.id END) as pending_expenses,
    COUNT(DISTINCT r.id) as total_reminders,
    COUNT(DISTINCT CASE WHEN r.notified = false THEN r.id END) as active_reminders
FROM users u
LEFT JOIN assets a ON u.id = a.user_id
LEFT JOIN expenses e ON u.id = e.user_id
LEFT JOIN reminders r ON a.id = r.asset_id
GROUP BY u.id, u.name;

COMMENT ON TABLE users IS 'User accounts and profiles';
COMMENT ON TABLE assets IS 'User assets (properties and vehicles)';
COMMENT ON TABLE expenses IS 'Expense tracking for assets';
COMMENT ON TABLE reminders IS 'Automated reminders for payments and deadlines';
COMMENT ON TABLE automations IS 'Automation settings per asset';
COMMENT ON TABLE documents IS 'Uploaded documents and OCR data';

-- Grant permissions for authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Completed schema setup
SELECT 'Casa&Più database schema created successfully!' as message;