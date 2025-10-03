// Admin user management actions
function makeUserAdmin(userId) {
    if (confirm('Make this user an admin? They will be able to access the admin panel and manage products.')) {
        // This would typically make an AJAX call to update the user
        // For now, we'll redirect to the edit page with a message
        window.location.href = `/admin/auth/user/${userId}/change/?make_admin=1`;
    }
}

function makeUserSuperuser(userId) {
    if (confirm('Make this user a superuser? They will have full admin privileges including managing other admin users.')) {
        // This would typically make an AJAX call to update the user
        // For now, we'll redirect to the edit page with a message
        window.location.href = `/admin/auth/user/${userId}/change/?make_superuser=1`;
    }
}

// Add helpful tooltips and styling
document.addEventListener('DOMContentLoaded', function() {
    // Add helpful messages to the admin interface
    const adminHelp = document.createElement('div');
    adminHelp.innerHTML = `
        <div style="background: #e7f3ff; border: 1px solid #b3d9ff; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <h3 style="margin-top: 0; color: #0066cc;">👤 Admin User Management</h3>
            <p><strong>To create an admin user:</strong></p>
            <ol>
                <li>Click "Add User" to create a new user</li>
                <li>Fill in username, email, and password</li>
                <li>Check "Staff status" to allow admin panel access</li>
                <li>Check "Superuser status" for full admin privileges (optional)</li>
                <li>Save the user</li>
            </ol>
            <p><strong>To make an existing user admin:</strong></p>
            <ol>
                <li>Find the user in the list below</li>
                <li>Click on their username to edit</li>
                <li>In the "Permissions" section, check "Staff status"</li>
                <li>Optionally check "Superuser status" for full privileges</li>
                <li>Save the changes</li>
            </ol>
            <p><em>Staff users can access admin panel and manage products. Superusers have all permissions.</em></p>
        </div>
    `;
    
    // Insert help text before the user list
    const changeList = document.querySelector('#changelist');
    if (changeList && window.location.pathname.includes('/auth/user/')) {
        changeList.parentNode.insertBefore(adminHelp, changeList);
    }
});
