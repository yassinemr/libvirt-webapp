from vrtManager import util 
 
 
def define_storage(conn, xml, flag):
        conn.storagePoolDefineXML(xml, flag)
        
def get_secrets(conn):
        return conn.listSecrets()

def create_storage(conn, stg_type, name, source, target,capacity):
        xml = """
                <pool type='%s'>
                <name>%s</name>""" % (stg_type, name)
        xml +="""<capacity unit='G'>%s</capacity>"""% (capacity)
        if stg_type == 'logical':
            xml += """
                  <source>
                    <device path='%s'/>
                    <name>%s</name>
                    <format type='lvm2'/>
                  </source>""" % (source, name)
        if stg_type == 'logical':
            target = '/dev/' + name
        xml += """
                  <target>
                       <path>%s</path>
                  </target>
                </pool>""" % target
        
        conn.storagePoolDefineXML(xml, 0)
        stg = conn.storagePoolLookupByName(name)
        if stg_type == 'logical':
            stg.build(0)
        stg.create(0)
        stg.setAutostart(1)

def create_volume_qcow2(conn,pool,name,capacity,path):
        pool = conn.storagePoolLookupByName(pool)

        stpVolXml="""<volume>
                <name>"""+name+""".qcow2</name>
                <capacity unit="MiB">"""+capacity+"""</capacity>
                <allocation unit="MiB">0</allocation>
                <target>
                <format type="qcow2"/>
                </target>
                <backingStore>
                <path>"""+path+"""</path>
                </backingStore>
                </volume>""" 

        pool.createXML(stpVolXml, 0)   
        
def create_volume_raw(conn,pool,name,capacity,allocation):

        pool = conn.storagePoolLookupByName(pool)
        
        stpVolXml="""<volume>
                        <name>"""+name+""".img</name>
                        <capacity unit="MiB">"""+capacity+"""</capacity>
                        <allocation unit="MiB">"""+allocation+"""</allocation>
                        <target>
                        <format type="raw"/>
                        </target>
                        </volume>
                        """
        pool.createXML(stpVolXml, 0)

def del_volume(pool, name):
        vol = pool.storageVolLookupByName(name)
        vol.delete(0)