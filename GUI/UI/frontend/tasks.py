def scheduled_job():
    f = open('/app/demo.txt','a')
    f.write("i'm running\n")
    f.close()