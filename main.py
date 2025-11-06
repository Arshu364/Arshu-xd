</div>
        '''
    
    is_active = user_tasks[task_id].get('active', False)
    logs = task_logs.get(task_id, [])
    
    # Reverse logs to show newest first
    reversed_logs = list(reversed(logs))
    
    return render_template_string(TASK_DETAILS_TEMPLATE,
        task_id=task_id,
        is_active=is_active,
        logs=reversed_logs[-100:]  # Show last 100 logs (newest first)
    )

if name == 'main':
    print("🔥 ARNAV MULTI-USER NONSTOP SERVER STARTED!")
    print("✅ Unlimited users can run simultaneously")
    print("✅ Auto token-to-cookies conversion for created another profiles")
    print("✅ Enhanced logging with full message content")
    print("✅ Beautiful Sukuna-themed animated background")
    print("✅ 24/7 nonstop operation guaranteed")
    print("✅ Secure - Users can only access their own data")
    app.run(host='0.0.0.0', port=5000, debug=False)
